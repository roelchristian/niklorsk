#!/usr/bin/env python3
"""Compatibility entry point for the staged vocabulary generator."""

import argparse
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the vocabulary with the tracked safe make pipeline.",
        epilog=(
            "Reads vocabulary/vocabulary.csv beside this script, regardless of the "
            "current directory. Generated vocabulary.tex and vocabulary_cleaned.csv "
            "remain in the fresh codex/builds/ directory printed by make. "
            "The structured CSV separates lemma, part of speech, gender, inflection group, "
            "definition, stress, perfect-auxiliary selection, accent and stress_anchor; legacy word/partofspeech/translation headers "
            "remain accepted. Stress records a positive citation-form syllable index. Accent is A1, A2 or blank; an optional one-based grapheme anchor disambiguates stress placement."
        ),
    )
    parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        return subprocess.run(["make", "vocab", "PYTHON=" + sys.executable], cwd=root).returncode
    except OSError as error:
        parser.exit(1, f"Could not run make vocab: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
