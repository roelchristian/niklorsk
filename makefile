# Safe, reproducible build for A Grammar of Niklorsk.
# Runtime helpers and every intermediate file stay in ignored codex/.
# No preexisting local helper files are required in a fresh checkout.
.DEFAULT_GOAL := all
PYTHON ?= python3
LATEX ?= lualatex
MAX_PASSES ?= 8
BUILD_TIMEOUT ?= 180
BUILD_FLAGS ?=
export NIKLORSK_ROOT := $(CURDIR)
export LATEX
export PYTHON

.PHONY: all book build check vocab clean distclean cleanup cleanup-preview bootstrap
all book build check vocab clean distclean cleanup cleanup-preview: bootstrap
	@"$${PYTHON}" "$(NIKLORSK_ROOT)/codex/build.py" $(if $(filter all book build,$@),build,$@) --root "$(NIKLORSK_ROOT)" --max-passes "$(MAX_PASSES)" --timeout "$(BUILD_TIMEOUT)" $(BUILD_FLAGS)

bootstrap:
	@"$${PYTHON}" -c 'import os; exec(os.environ["NIKLORSK_BOOTSTRAP_SOURCE"])'

define _NIKLORSK_BOOTSTRAP_SOURCE
from pathlib import Path
import os
import tempfile

folder = Path(os.environ["NIKLORSK_ROOT"]) / "codex"
if folder.is_symlink():
    raise SystemExit(f"Refusing local build/cleanup through symlink: {folder}")
folder.mkdir(exist_ok=True)
for name, key in (("build.py", "NIKLORSK_BUILD_SOURCE"), ("check_build.py", "NIKLORSK_CHECK_SOURCE"), ("cleanup.py", "NIKLORSK_CLEANUP_SOURCE")):
    fd, temporary = tempfile.mkstemp(prefix=".bootstrap-", suffix=".py", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(os.environ[key])
        os.replace(temporary, folder / name)
    finally:
        Path(temporary).unlink(missing_ok=True)
endef
export NIKLORSK_BOOTSTRAP_SOURCE := $(value _NIKLORSK_BOOTSTRAP_SOURCE)

define _NIKLORSK_BUILD_SOURCE
#!/usr/bin/env python3
"""Local, staged Niklorsk build. Never publish an unchecked manuscript."""

from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "codex"
CACHE = LOCAL / "cache"
BUILDS = LOCAL / "builds"
EXCLUDED_DIRS = {".git", "codex", ".venv", "venv", "archive", "__pycache__"}
SOURCE_SUFFIXES = {".tex", ".cls", ".sty", ".bib", ".bst", ".csv", ".png", ".jpg", ".jpeg", ".eps", ".pdf", ".otf", ".ttf"}
GENERATED = {"grammar.pdf", "grammar-tags.tex", "vocabulary/vocabulary.tex", "vocabulary/vocabulary_cleaned.csv"}
AUX_SUFFIXES = {".aux", ".toc", ".lot", ".lof", ".out", ".bbl", ".bcf", ".run.xml"}
POS = {
    "adj": "adjective", "adv": "adverb", "art": "article",
    "conj": "conjunction", "interj": "interjection", "n": "noun", "prep": "preposition",
    "pron": "pronoun", "v": "verb",
}
VOCABULARY_FIELDS = ["lemma", "partofspeech", "gender", "plurals", "definition", "stress"]
LEGACY_GENDERS = {"nm": "m", "nf": "f", "nn": "n"}
# Dictionary collation follows the requested Danish/Norwegian order, with ö
# in the place of ø. These equivalences affect sorting, never spelling.
DICTIONARY_ALPHABET = "abcdefghijklmnopqrstuvwxyzæöå"
DICTIONARY_WEIGHTS = {letter: index + 1 for index, letter in enumerate(DICTIONARY_ALPHABET)}
DICTIONARY_EQUIVALENTS = {"ä": "æ", "ø": "ö"}


class BuildError(Exception):
    pass


def source_files() -> list[Path]:
    files = []
    for folder, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith("."))
        for name in sorted(names):
            path = Path(folder) / name
            rel = path.relative_to(ROOT)
            if path.suffix.lower() in SOURCE_SUFFIXES and rel.as_posix() not in GENERATED:
                if path.is_symlink():
                    raise BuildError(f"Source symlinks are not supported: {rel}")
                files.append(rel)
    return sorted(files)


def source_digest(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for rel in files:
        digest.update(rel.as_posix().encode() + b"\0")
        digest.update((ROOT / rel).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def snapshot(stage: Path) -> str:
    files = source_files()
    before = source_digest(files)
    for rel in files:
        destination = stage / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, destination)
    copied = hashlib.sha256()
    for rel in files:
        copied.update(rel.as_posix().encode() + b"\0")
        copied.update((stage / rel).read_bytes())
        copied.update(b"\0")
    if before != copied.hexdigest() or before != source_digest(source_files()):
        raise BuildError("Grammar sources changed while taking the build snapshot; retry.")
    return before


def dictionary_key(text: str) -> tuple:
    """Collate canonical letter equivalents without altering their spelling."""
    text = unicodedata.normalize("NFC", text).casefold()
    return tuple(
        DICTIONARY_WEIGHTS.get(DICTIONARY_EQUIVALENTS.get(char, char), 100 + ord(char))
        for char in text if not char.isspace() and char != "-"
    )


def dictionary_heading(lemma: str) -> str:
    letter = unicodedata.normalize("NFC", lemma).casefold()[0]
    return DICTIONARY_EQUIVALENTS.get(letter, letter).upper()


def read_vocabulary(source: Path) -> list[dict]:
    """Read structured lexical records, accepting the original CSV headers."""
    entries = {}
    with source.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        legacy_fields = ["word", "partofspeech", "translation"]
        legacy = reader.fieldnames in (legacy_fields, legacy_fields + ["stress"])
        if not legacy and reader.fieldnames != VOCABULARY_FIELDS:
            raise BuildError(
                "Vocabulary needs lemma;partofspeech;gender;plurals;definition;stress "
                "or the legacy word;partofspeech;translation header with optional stress."
            )
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise BuildError(f"Malformed vocabulary row {line}: wrong number of columns.")
            row = {key: value.strip() for key, value in row.items()}
            stress = row.get("stress", "")
            if stress and (not stress.isascii() or not stress.isdecimal() or stress.startswith("0")):
                raise BuildError(f"Invalid stress on vocabulary row {line}: use a positive syllable index or leave blank.")
            pos = row["partofspeech"]
            allowed_pos = set(POS) | (set(LEGACY_GENDERS) if legacy else set())
            if pos and pos not in allowed_pos:
                raise BuildError(f"Unknown vocabulary part of speech on row {line}: {pos}.")
            if legacy:
                word = row["word"].replace(r'\\"a', "ä").replace(r'\\"o', "ö").replace(r"\\ae\{\}", "æ")
                forms = [form.strip() for form in word.split(",")]
                lemma, plurals = forms[0], forms[1:]
                gender = LEGACY_GENDERS.get(pos, "")
                pos = "n" if gender else pos
                definition = row["translation"]
            else:
                lemma, gender, definition = row["lemma"], row["gender"], row["definition"]
                plurals = [form.strip() for form in row["plurals"].split("|")] if row["plurals"] else []
            if "," in lemma or "|" in lemma:
                raise BuildError(f"Invalid lemma on vocabulary row {line}: put plural forms in the plurals field.")
            if pos == "n" and gender not in {"m", "f", "n"}:
                raise BuildError(f"Invalid noun gender on vocabulary row {line}: use m, f or n.")
            if pos != "n" and gender:
                raise BuildError(f"Unexpected gender on vocabulary row {line}: gender is recorded for nouns.")
            if any(not form or "," in form or "|" in form for form in plurals):
                raise BuildError(f"Invalid plural list on vocabulary row {line}: use nonempty forms separated by pipes.")
            if len(set(plurals)) != len(plurals):
                raise BuildError(f"Repeated plural form on vocabulary row {line}.")
            # Retain legacy incomplete-row compatibility after validating metadata.
            if legacy and not all(row[key] for key in legacy_fields):
                continue
            if not lemma or not pos or not definition:
                raise BuildError(f"Incomplete vocabulary row {line}: lemma, partofspeech and definition are required.")
            key = unicodedata.normalize("NFC", lemma).casefold(), pos
            entry = dict(lemma=lemma, partofspeech=pos, gender=gender, plurals=plurals, definition=definition, stress=stress)
            previous = entries.get(key)
            if previous:
                if previous["gender"] != gender or previous["definition"] != definition:
                    raise BuildError(f"Conflicting lexical records for {lemma} on vocabulary row {line}.")
                if previous["stress"] and stress and previous["stress"] != stress:
                    raise BuildError(f"Conflicting stress for {lemma} on vocabulary row {line}: {previous['stress']} and {stress}.")
                if not legacy:
                    raise BuildError(f"Duplicate lemma and part of speech on vocabulary row {line}: {lemma}; combine its plural variants in one row.")
                previous["stress"] = previous["stress"] or stress
                previous["plurals"].extend(form for form in plurals if form not in previous["plurals"])
            else:
                entries[key] = entry
    rows = sorted(entries.values(), key=lambda row: (
        dictionary_key(row["lemma"]), unicodedata.normalize("NFC", row["lemma"]).casefold(),
        row["lemma"], row["partofspeech"],
    ))
    if not rows:
        raise BuildError("Vocabulary has no complete entries.")
    return rows


def vocabulary(stage: Path) -> int:
    """Validate lexical records and generate the compact dictionary appendix."""
    rows = read_vocabulary(stage / "vocabulary/vocabulary.csv")
    outdir = stage / "vocabulary"
    with (outdir / "vocabulary_cleaned.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter=";", lineterminator="\n")
        writer.writerow(VOCABULARY_FIELDS)
        for row in rows:
            writer.writerow(["|".join(row[key]) if key == "plurals" else row[key] for key in VOCABULARY_FIELDS])
    used_pos = {row["partofspeech"] for row in rows}
    abbreviations = ["m. masculine", "f. feminine", "n. neuter"]
    abbreviations.extend(f"{key}. {value}" for key, value in POS.items() if key != "n" and key in used_pos)
    abbreviations.append("pl. plural")
    legend = r"~\textperiodcentered{} ".join(abbreviations)
    # Initialise columns using the vocabulary font's baseline metrics.
    lines = [
        "% Generated locally from vocabulary/vocabulary.csv. Do not edit.",
        r"\chapter*{Vocabulary}",
        r"\addcontentsline{toc}{chapter}{Vocabulary}",
        r"\markboth{Vocabulary}{Vocabulary}",
        r"{\footnotesize\noindent " + legend + r"\par}",
        "",
        r"{\footnotesize\noindent A superscript numeral marks primary stress on a syllable of the lemma, counted from the first syllable. An unmarked entry has no individual stress specification; see Chapter~\ref{chap:phonology}, \S\ref{sec:stress-prosody}. Entries follow A--Z, Æ (including Ä), Ö, Å.\par}",
        "", r"{\footnotesize", r"\begin{multicols}{2}", "",
    ]
    previous = ""
    for row in rows:
        letter = dictionary_heading(row["lemma"])
        new_letter = letter != previous
        if new_letter:
            lines.extend([
                r"\begingroup",
                r"\noindent\begin{minipage}{\linewidth}",
                r"\vocabcentered{" + letter + "}", "",
            ])
        label = row["gender"] + "." if row["partofspeech"] == "n" else row["partofspeech"] + "."
        plurals = ["unchanged" if form == row["lemma"] else form for form in row["plurals"]]
        arguments = [row["lemma"], row["stress"], label, ", ".join(plurals), row["definition"]]
        lines.extend([r"\dictionaryentry" + "".join("{" + value + "}" for value in arguments), ""])
        if new_letter:
            lines.extend([r"\end{minipage}\par", r"\endgroup", ""])
        previous = letter
    lines.extend([r"\end{multicols}", "}", ""])
    (outdir / "vocabulary.tex").write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


def aux_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*") if path.is_file() and (path.suffix in AUX_SUFFIXES or path.name == "grammar-tags.tex"))


def aux_digest(stage: Path) -> str:
    digest = hashlib.sha256()
    for path in aux_files(stage):
        digest.update(path.relative_to(stage).as_posix().encode() + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def seed_cache(stage: Path, key: str) -> None:
    folder = CACHE / "aux" / key
    if not folder.is_dir():
        return
    for path in aux_files(folder):
        rel = path.relative_to(folder)
        if rel.suffix == ".aux" and not (stage / rel.with_suffix(".tex")).is_file():
            continue
        destination = stage / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    os.utime(folder, None)  # Retention uses last successful reuse, not creation.


def save_cache(stage: Path, key: str) -> None:
    (CACHE / "aux").mkdir(exist_ok=True)
    fresh = Path(tempfile.mkdtemp(prefix="aux-", dir=CACHE))
    for path in aux_files(stage):
        destination = fresh / path.relative_to(stage)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    old = CACHE / "aux" / key
    if old.exists():
        shutil.rmtree(old)
    fresh.rename(old)


def save_font_cache(stage: Path) -> None:
    for name in ("texmf-var", "luatex-cache", "xdg-cache"):
        source = stage / name
        if source.is_dir():
            shutil.copytree(source, CACHE / name, dirs_exist_ok=True)
            os.utime(CACHE / name, None)


def environment(stage: Path) -> dict[str, str]:
    env = os.environ.copy()
    # The tracked Makefile may bootstrap these helpers through exported text.
    # Do not propagate that large implementation payload to TeX/backend tools.
    for key in list(env):
        if key.startswith("NIKLORSK_") and key.endswith("_SOURCE"):
            env.pop(key)
    # Seed reusable font data into stage-local paths: TeX disallows absolute
    # output paths under openout_any=p. Keep that restriction enabled.
    locations = {
        "TEXMFVAR": stage / "texmf-var", "TEXMFCONFIG": stage / "texmf-config",
        "TEXMFCACHE": stage / "luatex-cache", "XDG_CACHE_HOME": stage / "xdg-cache",
        "TMPDIR": stage / "tmp",
    }
    for key, path in locations.items():
        path.mkdir(parents=True, exist_ok=True)
        if key in {"TEXMFVAR", "TEXMFCACHE", "XDG_CACHE_HOME"}:
            cached = CACHE / path.name
            if cached.is_dir():
                shutil.copytree(cached, path, dirs_exist_ok=True)
                os.utime(cached, None)
        env[key] = str(path.relative_to(stage)) if key.startswith("TEXMF") else str(path)
    env["TEXINPUTS"] = str(stage) + os.pathsep
    env["BIBINPUTS"] = str(stage) + os.pathsep
    return env


def run_bibliography(stage: Path, env: dict[str, str], previous: str | None, timeout: float) -> str | None:
    bcf = stage / "grammar.bcf"
    aux = stage / "grammar.aux"
    if bcf.is_file():
        name, data = "biber", bcf.read_bytes()
    elif aux.is_file() and any(b"\\bibdata" in path.read_bytes() for path in stage.rglob("*.aux")):
        name = "bibtex"
        data = b"\0".join(path.read_bytes() for path in sorted(stage.rglob("*.aux")))
    else:
        return None
    digest = name + ":" + hashlib.sha256(data).hexdigest()
    if digest == previous:
        return previous
    executable = shutil.which(name)
    if executable is None:
        raise BuildError(f"Bibliography requires {name}, but the executable is not available.")
    logfile = stage / f"{name}-output.log"
    with logfile.open("a", encoding="utf-8") as stream:
        result = subprocess.run([executable, "grammar"], cwd=stage, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode:
        raise BuildError(f"{name} failed (exit {result.returncode}). See {logfile}")
    return digest


def atomic_report(report: dict) -> None:
    destination = LOCAL / "last-build.json"
    temporary = LOCAL / "last-build.json.tmp"
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination)


def build(args: argparse.Namespace) -> int:
    stage = Path(tempfile.mkdtemp(prefix=time.strftime("%Y%m%d-%H%M%S-"), dir=BUILDS))
    report = {"ok": False, "action": args.action, "stage": str(stage), "published": False}
    print(f"Staging build: {stage}", flush=True)
    try:
        original_digest = snapshot(stage)
        report["source_sha256"] = original_digest
        report["vocabulary_entries"] = vocabulary(stage)
        if args.action == "vocab":
            report["ok"] = True
            print(f"Vocabulary generated in {stage / 'vocabulary'}", flush=True)
            return 0
        helper_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        cache_key = hashlib.sha256((original_digest + helper_digest + args.engine).encode()).hexdigest()
        if not args.no_cache:
            seed_cache(stage, cache_key)
        env = environment(stage)
        engine = shutil.which(args.engine)
        if engine is None:
            raise BuildError(f"LuaLaTeX executable not found: {args.engine}")
        previous = aux_digest(stage)
        stable = False
        bibliography = None
        for number in range(1, args.max_passes + 1):
            print(f"LuaLaTeX pass {number}/{args.max_passes}", flush=True)
            logfile = stage / f"lualatex-pass-{number:02d}.log"
            with logfile.open("w", encoding="utf-8") as stream:
                result = subprocess.run(
                    [engine, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", "-recorder", "grammar.tex"],
                    cwd=stage, env=env, stdout=stream, stderr=subprocess.STDOUT,
                    timeout=args.timeout,
                )
            report["passes"] = number
            if result.returncode:
                tail = "\n".join(logfile.read_text(errors="replace").splitlines()[-22:])
                raise BuildError(f"LuaLaTeX failed (exit {result.returncode}).\n{tail}\nFull log: {logfile}")
            bibliography = run_bibliography(stage, env, bibliography, args.timeout)
            current = aux_digest(stage)
            if number >= 2 and previous == current:
                stable = True
                break
            previous = current
        if not stable:
            raise BuildError(f"References/auxiliary files did not converge after {args.max_passes} passes.")
        from check_build import validate_build
        validation = validate_build(stage, jobname="grammar")
        report["validation"] = validation
        (stage / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
        if not validation["ok"]:
            messages = "\n".join(str(item.get("message", item)) for item in validation["errors"])
            raise BuildError(f"Build checks failed:\n{messages}\nReport: {stage / 'validation.json'}")
        save_font_cache(stage)
        if not args.no_cache:
            save_cache(stage, cache_key)
        # Prepare reports and publication data before the final source check.
        report["ok"] = True
        atomic_report(report)
        (stage / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.action == "build":
            # Stage and destination are on the same filesystem. The old PDF
            # remains in place until this single atomic operation succeeds.
            candidate = stage / "publish.pdf"
            shutil.copyfile(stage / "grammar.pdf", candidate)
            with candidate.open("rb") as stream:
                os.fsync(stream.fileno())
            if original_digest != source_digest(source_files()):
                raise BuildError("Grammar sources changed during the build; the published PDF was preserved. Retry.")
            os.replace(candidate, ROOT / "grammar.pdf")
            report["published"] = True
            try:
                print(f"Validated and published: {ROOT / 'grammar.pdf'}", flush=True)
            except OSError:
                pass  # A closed output pipe cannot undo a completed publication.
        else:
            if original_digest != source_digest(source_files()):
                raise BuildError("Grammar sources changed during the build; retry.")
            print(f"Validated without publishing: {stage / 'grammar.pdf'}", flush=True)
        return 0
    except (BuildError, OSError, subprocess.SubprocessError) as error:
        report["ok"] = False
        report["error"] = str(error)
        print(f"Build failed; grammar.pdf was not replaced.\n{error}", file=sys.stderr)
        return 1
    finally:
        # Persistent font data was saved only after validation. Successful
        # stages retain sources/PDF/logs, without another full cache copy.
        if report["ok"]:
            for name in ("texmf-var", "luatex-cache", "xdg-cache", "texmf-config", "tmp"):
                try:
                    if (stage / name).exists():
                        shutil.rmtree(stage / name)
                except OSError as error:
                    print(f"Could not trim stage cache {name}: {error}", file=sys.stderr)
        try:
            atomic_report(report)
            (stage / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        except OSError as error:
            # Reporting must never turn a successful atomic publication into
            # a claimed failure or imply the incumbent was left unchanged.
            print(f"Could not persist final diagnostics (published={report['published']}): {error}", file=sys.stderr)


def main() -> int:
    global ROOT, LOCAL, CACHE, BUILDS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=["build", "check", "vocab", "clean", "distclean", "cleanup", "cleanup-preview"], default="build")
    parser.add_argument("--root", type=Path, default=ROOT, help="Grammar project directory (also useful for isolated checks)")
    parser.add_argument("--engine", default=os.environ.get("LATEX", "lualatex"))
    parser.add_argument("--max-passes", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=180, help="Maximum seconds per LuaLaTeX pass")
    parser.add_argument("--no-cache", action="store_true", help="Do not reuse or save auxiliary files")
    parser.add_argument("--dry-run", action="store_true", help="Preview cleanup without deleting artifacts (cleanup only)")
    args = parser.parse_args()
    if args.max_passes < 2 or args.timeout <= 0:
        parser.error("--max-passes must be at least 2 and --timeout must be positive")
    if args.dry_run and args.action not in {"cleanup", "cleanup-preview"}:
        parser.error("--dry-run is only available for cleanup")
    ROOT = args.root.resolve()
    LOCAL = ROOT / "codex"
    CACHE = LOCAL / "cache"
    BUILDS = LOCAL / "builds"
    if not (ROOT / "grammar.tex").is_file():
        parser.error(f"No grammar.tex in project directory: {ROOT}")
    for path in (LOCAL, BUILDS, CACHE, CACHE / "aux", LOCAL / "build.lock"):
        if path.is_symlink():
            parser.error(f"Refusing local build/cleanup through symlink: {path}")
    LOCAL.mkdir(exist_ok=True)
    with (LOCAL / "build.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Another local build is running; try again after it finishes.", file=sys.stderr)
            return 1
        if args.action in {"clean", "distclean"}:
            for folder in ((BUILDS, CACHE) if args.action == "distclean" else (BUILDS,)):
                if folder.exists():
                    shutil.rmtree(folder)
            (LOCAL / "last-build.json").unlink(missing_ok=True)
            print("Removed local builds" + (" and caches." if args.action == "distclean" else "; reusable caches retained.") + " Published grammar.pdf was preserved.")
            return 0
        from cleanup import cleanup, summarize
        if args.action in {"cleanup", "cleanup-preview"}:
            try:
                result = cleanup(LOCAL, dry_run=args.dry_run or args.action == "cleanup-preview")
                summarize(result, verbose=True)
                return int(any(group["errors"] for group in result["groups"].values()))
            except (OSError, ValueError) as error:
                print(f"Cleanup failed: {error}", file=sys.stderr)
                return 1
        def maintain() -> None:
            try:
                summarize(cleanup(LOCAL))
            except (OSError, ValueError) as error:
                print(f"Cleanup skipped: {error}", file=sys.stderr)
        maintain()
        BUILDS.mkdir(parents=True, exist_ok=True)
        CACHE.mkdir(parents=True, exist_ok=True)
        try:
            return build(args)
        finally:
            maintain()


if __name__ == "__main__":
    raise SystemExit(main())
endef
export NIKLORSK_BUILD_SOURCE := $(value _NIKLORSK_BUILD_SOURCE)

define _NIKLORSK_CHECK_SOURCE
#!/usr/bin/env python3
"""Validate one completed, staged Niklorsk build before it is published.

This helper deliberately never writes the project PDF. It reads only the staged
build and writes a report only when --report is explicitly supplied.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


def _issue(kind: str, message: str, source: str, line: int | None = None) -> dict[str, Any]:
    return {"kind": kind, "message": message, "source": source, "line": line}


def check_log(text: str, source: str = "grammar.log") -> tuple[list[dict], list[dict]]:
    """Check only the final pass log; earlier-pass warnings are expected."""
    errors: list[dict] = []
    warnings: list[dict] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        number = index + 1
        if re.match(r"^Overfull \\[hv]box\b", line):
            errors.append(_issue("overfull-box", line.strip(), source, number))
        elif re.match(r"^Underfull \\[hv]box\b", line):
            warnings.append(_issue("underfull-box", line.strip(), source, number))
        if "Missing character:" in line:
            errors.append(_issue("missing-glyph", line.strip(), source, number))
        if line.startswith("!") or re.search(
            r":\d+:\s*(?:LaTeX Error|Package \S+ Error|Undefined control sequence|"
            r"Emergency stop|Missing .+ inserted|Extra .+|Runaway argument)", line
        ):
            errors.append(_issue("tex-error", line.strip(), source, number))
        if "Fatal error occurred" in line or "Emergency stop" in line:
            errors.append(_issue("tex-fatal", line.strip(), source, number))
        if "Warning:" not in line:
            continue
        block = [line.strip()]
        for continuation in lines[index + 1:index + 8]:
            if not continuation.strip() or "Warning:" in continuation:
                break
            block.append(continuation.strip())
        message = " ".join(block)
        # Package prefixes may separate words across wrapped log lines.
        normalized = re.sub(r"\([^)]*\)\s*", " ", message)
        if (
            re.search(r"(?:Reference|Citation)\b.*?\bundefined\b", normalized, re.I)
            or re.search(r"undefined (?:references|citations)", normalized, re.I)
            or re.search(r"entry could not be found in the database", normalized, re.I)
        ):
            errors.append(_issue("unresolved-reference", message, source, number))
        elif re.search(r"multiply[- ]defined|multiply defined", normalized, re.I):
            errors.append(_issue("duplicate-label", message, source, number))
        elif re.search(
            r"\brerun\b|\bre-run\b|please\s+\(re\)run|please\s+run\s+(?:biber|bibtex)|"
            r"label.*may have changed|table widths have changed", message, re.I
        ):
            errors.append(_issue("not-converged", message, source, number))
        else:
            warnings.append(_issue("latex-warning", message, source, number))
    if not re.search(r"Output written on .+\.pdf\s*\(", text):
        errors.append(_issue("incomplete-tex-run", "Final log has no successful PDF output record.", source))
    return errors, warnings


def check_aux(build_dir: Path, jobname: str = "grammar") -> tuple[list[dict], int]:
    """Follow the main auxiliary-file graph rather than scanning stale caches."""
    errors: list[dict] = []
    labels: dict[str, tuple[str, int]] = {}
    visited: set[Path] = set()
    build_dir = build_dir.resolve()

    def visit(path: Path) -> None:
        path = path.resolve()
        if not path.is_relative_to(build_dir):
            errors.append(_issue("aux-path", "Auxiliary input points outside the staged build.", str(path)))
            return
        if path in visited:
            return
        visited.add(path)
        relative = str(path.relative_to(build_dir))
        if not path.is_file():
            errors.append(_issue("missing-aux", "Missing auxiliary file from the active include graph.", relative))
            return
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            for label in re.findall(r"\\newlabel\{([^}]+)\}", line):
                if label in labels:
                    previous, previous_line = labels[label]
                    errors.append(_issue(
                        "duplicate-label", f"Label {label!r} already appears at {previous}:{previous_line}.",
                        relative, number,
                    ))
                else:
                    labels[label] = (relative, number)
            for included in re.findall(r"\\@input\{([^}]+)\}", line):
                # TeX resolves these names against its working directory.
                visit(build_dir / included)

    visit(build_dir / f"{jobname}.aux")
    return errors, len(labels)


def check_pdf(path: Path) -> tuple[list[dict], list[dict], dict[str, Any]]:
    errors: list[dict] = []
    warnings: list[dict] = []
    metrics: dict[str, Any] = {}
    if not path.is_file():
        return [_issue("missing-pdf", "The staged PDF was not created.", path.name)], warnings, metrics
    size = path.stat().st_size
    metrics["pdf_bytes"] = size
    with path.open("rb") as stream:
        header = stream.read(8)
        stream.seek(max(0, size - 2048))
        tail = stream.read()
    if not header.startswith(b"%PDF-") or b"%%EOF" not in tail:
        errors.append(_issue("incomplete-pdf", "PDF header or final EOF marker is missing.", path.name))
        return errors, warnings, metrics
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo is None:
        # Structural PDF inspection is mandatory, so an absent tool cannot
        # silently downgrade a publication gate to a header-only check.
        errors.append(_issue("missing-pdf-validator", "Install pdfinfo (Poppler) to inspect the completed PDF.", path.name))
        return errors, warnings, metrics
    try:
        result = subprocess.run(
            [pdfinfo, str(path)], capture_output=True, text=True, timeout=60, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(_issue("pdf-inspection", f"Unable to inspect PDF: {exc}", path.name))
        return errors, warnings, metrics
    if result.returncode != 0:
        errors.append(_issue("invalid-pdf", result.stderr.strip() or "pdfinfo rejected the PDF.", path.name))
        return errors, warnings, metrics
    if result.stderr.strip():
        errors.append(_issue("pdf-parser-error", result.stderr.strip(), path.name))
    pages = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.M)
    if pages is None or int(pages.group(1)) < 1:
        errors.append(_issue("empty-pdf", "PDF does not contain a positive page count.", path.name))
    else:
        metrics["pages"] = int(pages.group(1))
    page_size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", result.stdout, re.M)
    if page_size:
        metrics["page_size_pt"] = [float(page_size.group(1)), float(page_size.group(2))]
        if min(metrics["page_size_pt"]) <= 0:
            errors.append(_issue("page-size", "PDF page dimensions must be positive.", path.name))
    return errors, warnings, metrics


def check_caption_labels(build_dir: Path, jobname: str) -> list[dict]:
    """Reject unambiguous wrong-number float labels in active source files."""
    errors: list[dict] = []
    build_dir = build_dir.resolve()
    visited: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in visited or not path.is_relative_to(build_dir) or not path.is_file():
            return
        visited.add(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        # Keep line numbers while ignoring commented-out source.
        text = re.sub(r"(?<!\\)%[^\n]*", "", text)
        for match in re.finditer(r"\\begin\{(table\*?|figure\*?)\}(.*?)\\end\{\1\}", text, re.S):
            block = match.group(2)
            caption = block.find(r"\caption")
            label = block.find(r"\label")
            # Subfloats can legitimately establish their own counter before the
            # enclosing float caption. Do not guess about those arrangements.
            prefix = block[:caption] if caption >= 0 else block
            if re.search(r"\\(?:begin\{(?:subfigure|subtable)\}|subfloat\b)", prefix):
                continue
            if 0 <= label < caption:
                number = text.count("\n", 0, match.start(2) + label) + 1
                errors.append(_issue(
                    "label-before-caption", "Move the float label after its caption so references use the float number.",
                    str(path.relative_to(build_dir)), number,
                ))
        for included in re.findall(r"\\(?:include|input)\{([^}]+)\}", text):
            included_path = Path(included)
            if included_path.suffix == "":
                included_path = included_path.with_suffix(".tex")
            visit(build_dir / included_path)

    visit(build_dir / f"{jobname}.tex")
    return errors


def validate_build(build_dir: Path, jobname: str = "grammar") -> dict[str, Any]:
    build_dir = Path(build_dir).resolve()
    errors: list[dict] = []
    warnings: list[dict] = []
    log = build_dir / f"{jobname}.log"
    if log.is_file():
        log_errors, log_warnings = check_log(log.read_text(encoding="utf-8", errors="replace"), log.name)
        errors.extend(log_errors)
        warnings.extend(log_warnings)
    else:
        errors.append(_issue("missing-log", "Final LaTeX log is missing.", log.name))
    aux_errors, label_count = check_aux(build_dir, jobname)
    errors.extend(aux_errors)
    pdf_errors, pdf_warnings, metrics = check_pdf(build_dir / f"{jobname}.pdf")
    errors.extend(pdf_errors)
    warnings.extend(pdf_warnings)
    errors.extend(check_caption_labels(build_dir, jobname))
    return {
        "ok": not errors,
        "build_dir": str(build_dir),
        "jobname": jobname,
        "errors": errors,
        "warnings": warnings,
        "summary": {"errors": len(errors), "warnings": len(warnings), "labels": label_count, **metrics},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("--jobname", default="grammar")
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    report = validate_build(arguments.build_dir, arguments.jobname)
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for severity in ("errors", "warnings"):
        for issue in report[severity][:20]:
            location = issue["source"] + (f':{issue["line"]}' if issue["line"] else "")
            print(f'{severity[:-1].upper()}: {location}: [{issue["kind"]}] {issue["message"]}')
        if len(report[severity]) > 20:
            print(f'{len(report[severity]) - 20} more {severity}; use --report for all diagnostics.')
    summary = report["summary"]
    print(f'Build checks: {summary["errors"]} errors, {summary["warnings"]} warnings; {summary["labels"]} labels.')
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
endef
export NIKLORSK_CHECK_SOURCE := $(value _NIKLORSK_CHECK_SOURCE)

define _NIKLORSK_CLEANUP_SOURCE
#!/usr/bin/env python3
"""Age/size retention for ignored local artifacts; called with build.lock held."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import math
import os
from pathlib import Path
import shutil
import stat
import tempfile
import time

MIB = 1024 * 1024
DAY = 86400
DEFAULTS = {
    "artifacts": {"days": 10, "mib": 192, "grace_hours": 24},
    "builds": {"days": 5, "mib": 96, "count": 8},
    "aux": {"days": 21, "mib": 24, "count": 6},
    "fonts": {"days": 60, "mib": 96},
}
FONT_DIRS = ("texmf-var", "luatex-cache", "xdg-cache")
DURABLE_SUFFIXES = {".md", ".patch", ".py", ".sh", ".mk", ".toml", ".yaml", ".yml"}
RESERVED = {"builds", "cache", "archive", "build.lock", "last-build.json",
            "last-build.json.tmp", "cleanup-policy.json", "cleanup-report.json"}


@dataclass
class Entry:
    path: Path
    size: int
    modified: float
    protected: bool = False
    children: tuple = ()
    pinned: bool = False


def inspect(path: Path, durable: bool = False) -> Entry:
    """Never follow links, including links inside an otherwise disposable tree."""
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
        return Entry(path, 0, info.st_mtime, True)
    if stat.S_ISREG(info.st_mode):
        keep = durable and (path.suffix.lower() in DURABLE_SUFFIXES or path.name in {"Makefile", "makefile"})
        return Entry(path, info.st_size, info.st_mtime, keep)
    children = tuple(inspect(child, durable) for child in sorted(path.iterdir()))
    pinned = any(child.path.name == ".cleanup-keep" for child in children)
    # Keep a reusable tool/virtual environment intact, rather than pruning
    # individual dependencies whose original timestamps predate the fixture.
    tool = durable and any(child.path.name == "pyvenv.cfg" or child.path.suffix in {".py", ".sh"}
                           for child in children)
    pinned = pinned or tool
    return Entry(path, sum(child.size for child in children),
                 max([info.st_mtime, *(child.modified for child in children)]),
                 pinned or any(child.protected for child in children), children, pinned)


def candidates(entry: Entry, modified: float = 0):
    modified = max(modified, entry.modified)
    if not entry.protected:
        yield replace(entry, modified=modified)
    elif entry.children and not entry.pinned:
        for child in entry.children:
            yield from candidates(child, modified)


def policy(local: Path) -> dict:
    result = {name: values.copy() for name, values in DEFAULTS.items()}
    path = local / "cleanup-policy.json"
    if not path.exists():
        return result
    overrides = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(overrides, dict) or set(overrides) - set(result):
        raise ValueError("cleanup-policy.json: unknown retention group")
    for name, values in overrides.items():
        if not isinstance(values, dict) or set(values) - set(result[name]):
            raise ValueError(f"cleanup-policy.json: unknown option in {name}")
        for key, value in values.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"cleanup-policy.json: {name}.{key} must be a finite nonnegative number")
            if key == "count" and (not isinstance(value, int) or value < 1):
                raise ValueError(f"cleanup-policy.json: {name}.count must be a positive integer")
            result[name][key] = value
    return result


def read_report(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def retained_builds(local: Path, entries: list[Entry]) -> set[Path]:
    """Retain the last attempt, last validated PDF, and last failure."""
    retained = set()
    last = read_report(local / "last-build.json").get("stage")
    if isinstance(last, str):
        retained.update(entry.path for entry in entries if str(entry.path) == last)
    found = set()
    for entry in sorted(entries, key=lambda item: (item.modified, item.path.name), reverse=True):
        if not entry.children or entry.path.is_symlink():
            continue
        report = read_report(entry.path / "build-report.json")
        if report.get("ok") is True and report.get("action") in {"build", "check"}:
            kind = "validated"
        elif report.get("ok") is False:
            kind = "failed"
        else:
            continue
        if kind not in found:
            found.add(kind)
            retained.add(entry.path)
    return retained


def prune(name: str, entries: list[Entry], rules: dict, now: float,
          retained: set[Path], dry_run: bool, local: Path, protected_bytes: int = 0) -> dict:
    before = protected_bytes + sum(entry.size for entry in entries)
    remaining = before
    count = len(entries)
    removed = []
    errors = []
    for entry in sorted(entries, key=lambda item: (item.modified, str(item.path))):
        if entry.protected or entry.path in retained:
            continue
        age = now - entry.modified
        expired = age > rules["days"] * DAY
        pressure = remaining > rules["mib"] * MIB or count > rules.get("count", math.inf)
        if not (expired or pressure) or age < rules.get("grace_hours", 0) * 3600:
            continue
        try:
            if not dry_run:
                # No shell globs or resolved link targets; all paths came from
                # lstat walks of the three checked local containers.
                if entry.children or entry.path.is_dir():
                    shutil.rmtree(entry.path)
                else:
                    entry.path.unlink()
            removed.append({"path": str(entry.path.relative_to(local)), "bytes": entry.size,
                            "reason": "age" if expired else "size/count"})
            remaining -= entry.size
            count -= 1
        except OSError as error:
            errors.append(f"{entry.path}: {error}")
    return {"before_bytes": before, "after_bytes": remaining, "removed": removed,
            "over_budget": remaining > rules["mib"] * MIB or count > rules.get("count", math.inf),
            "errors": errors}


def cleanup(local: Path, dry_run: bool = False, now: float | None = None) -> dict:
    """Caller holds the same lock as builds/clean; limits are separate budgets."""
    now = time.time() if now is None else now
    for path in (local, local / "builds", local / "cache", local / "cache/aux"):
        if path.is_symlink():
            raise ValueError(f"Refusing cleanup through symlink: {path}")
    rules = policy(local)  # Validate everything before the first deletion.
    builds = [inspect(path) for path in (local / "builds").iterdir()] if (local / "builds").exists() else []
    aux = [inspect(path) for path in (local / "cache/aux").iterdir()] if (local / "cache/aux").exists() else []
    fonts = [inspect(local / "cache" / name) for name in FONT_DIRS if (local / "cache" / name).exists()]
    # Keep a warm bundle when it fits. Oversized regenerable caches may be
    # evicted as a unit rather than growing indefinitely or leaving partial data.
    fresh_fonts = [entry for entry in fonts if 0 < entry.size <= rules["fonts"]["mib"] * MIB
                   and now - entry.modified <= rules["fonts"]["days"] * DAY]
    keep_fonts = {max(fresh_fonts, key=lambda item: item.modified).path} if fresh_fonts else set()
    artifacts = [inspect(path, durable=True) for path in local.iterdir() if path.name not in RESERVED]
    disposable = [item for entry in artifacts for item in candidates(entry)]
    protected = sum(entry.size for entry in artifacts) - sum(entry.size for entry in disposable)
    groups = {
        "builds": prune("builds", builds, rules["builds"], now, retained_builds(local, builds), dry_run, local),
        "aux": prune("aux", aux, rules["aux"], now, set(), dry_run, local),
        "fonts": prune("fonts", fonts, rules["fonts"], now, keep_fonts, dry_run, local),
        "artifacts": prune("artifacts", disposable, rules["artifacts"], now, set(), dry_run, local, protected),
    }
    # Remove obsolete cache names and interrupted aux-save temporary trees with
    # the same age/size policy, without treating them as live font data.
    extras = [inspect(path) for path in (local / "cache").iterdir()
              if path.name not in {*FONT_DIRS, "aux"}] if (local / "cache").exists() else []
    groups["cache_scratch"] = prune("cache_scratch", extras, rules["aux"], now, set(), dry_run, local)
    report = {"dry_run": dry_run, "time": now, "policy": rules, "groups": groups}
    if not dry_run:
        descriptor, name = tempfile.mkstemp(prefix=".cleanup-report-", suffix=".tmp", dir=local)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(report, indent=2) + "\n")
            os.replace(temporary, local / "cleanup-report.json")
        finally:
            temporary.unlink(missing_ok=True)
    return report


def summarize(report: dict, verbose: bool = False) -> None:
    groups = report["groups"]
    removed = sum(len(group["removed"]) for group in groups.values())
    saved = sum(group["before_bytes"] - group["after_bytes"] for group in groups.values())
    print(f"Cleanup {'preview' if report['dry_run'] else 'complete'}: {removed} items, {saved / MIB:.1f} MiB {'reclaimable' if report['dry_run'] else 'reclaimed'}.")
    for name, group in groups.items():
        if verbose:
            print(f"  {name}: {group['before_bytes'] / MIB:.1f} -> {group['after_bytes'] / MIB:.1f} MiB")
            for item in group["removed"]:
                print(f"    {item['path']} ({item['reason']})")
        if group["over_budget"]:
            print(f"  {name}: retention limit exceeded; protected/recent items retained.")
        for error in group["errors"]:
            print(f"  Cleanup warning: {error}")
endef
export NIKLORSK_CLEANUP_SOURCE := $(value _NIKLORSK_CLEANUP_SOURCE)
