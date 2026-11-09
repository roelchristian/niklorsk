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
            "The optional stress column records a positive lemma syllable index."
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
