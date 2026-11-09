#!/bin/sh
# Publish only a validated grammar, then atomically save a local dated copy.
set -eu

cd -- "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
make all

archive_dir="codex/archive"
mkdir -p "$archive_dir"
temporary=$(mktemp "$archive_dir/.grammar-XXXXXXXX")
trap 'rm -f "$temporary"' EXIT HUP INT TERM
cp grammar.pdf "$temporary"
mv -f "$temporary" "$archive_dir/grammar-$(date +%Y-%m-%d).pdf"
