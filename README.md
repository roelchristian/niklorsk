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

Install Python 3, a TeX distribution with LuaLaTeX and the packages used by
`grammarstyle.cls`, and Noto Sans (regular, semibold, italic, and semibold italic).
Run these commands from the project directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
make all
```

`make all` regenerates the vocabulary and runs LuaLaTeX twice, producing
`grammar.pdf`. Use `make vocab` to regenerate only the vocabulary or `make book`
for a single LuaLaTeX pass after the vocabulary has been generated.

`./archive.sh` builds the grammar, saves a dated PDF in `archive/`, and removes
auxiliary files. Generated files and the local Python environment are ignored
by Git.
