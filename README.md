# A Grammar of Niklorsk

LaTeX sources for *A Grammar of Niklorsk* by Roel Christian Yambao.

## Contents

- `grammar.tex`: manuscript entry point.
- `chapters/`: phonology, verbs, nouns, modifiers, clause structure, derivations, and sample texts.
- `grammarstyle.cls` and `preamble/`: typography and glossing commands.
- `vocabulary/vocabulary.csv`: source vocabulary; edit this file to update the word list.
- `vocab-parser.py`: generates the vocabulary appendix and a cleaned CSV.
- `texts/`: additional translation drafts and a small Niklorsk–English corpus, kept outside the compiled manuscript.

## Build

Install Python 3.9 or newer, a TeX distribution with LuaLaTeX and the packages
used by `grammarstyle.cls`, Poppler's `pdfinfo`, and Noto Sans (regular,
semibold, italic, and semibold italic). Run from the project directory:

```sh
make
```

The tracked makefile creates its runtime helpers under `codex/`, snapshots the
grammar sources into a fresh temporary build directory, and generates the
vocabulary there without external Python dependencies. LuaLaTeX runs until
references and auxiliary files converge. Bibliography processing, when needed,
also runs inside the temporary directory.

Publication requires a valid, nonempty PDF, resolved and correctly numbered
references, no duplicate labels, no rerun requests, no missing glyphs, and no
overfull boxes. Underfull boxes and other warnings appear in the validation
report. Only after these checks pass does one atomic replacement publish
`grammar.pdf` in the root. A failed or interrupted build preserves the previous
PDF. Concurrent builds are rejected, and source edits during a build require a
new build.

- `make`, `make all`, and `make book`: build, validate, and publish.
- `make check`: perform the full staged build and checks without publishing.
- `make vocab`: generate vocabulary files in a temporary build directory.
- `make clean`: remove local builds and caches, preserving `grammar.pdf`.
- `make BUILD_FLAGS=--no-cache`: build without reusing auxiliary files.

Builds, logs, bibliography files, font/TeX caches, and validation reports stay
under `codex/`; `codex/last-build.json` points to the latest diagnostics.
`./archive.sh` validates the grammar and saves a dated PDF under
`codex/archive/`.

`codex/` and the root `agents.md` are ignored by Git and remain local. The
standalone legacy `vocab-parser.py` still uses `requirements.txt`; the makefile
does not require it.
