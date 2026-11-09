#!/bin/bash

#define AUX_EXTS array var: aux out ilg ind log lot lof maf mtc mtc0 xml toc ent lg dvi idv 4ct 4tc acn acr alg bbl bcf blg lpz lzo lzs ist
AUX_EXTS="aux out ilg ind lot lof maf mtc mtc0 xml toc ent lg dvi idv 4ct 4tc acn acr alg bbl bcf blg lpz lzo lzs ist"

# Capture the start time
START_TIME=$(date +%s)

# Define the current date in the format YYYY-MM-DD
DATE=$(date +%Y-%m-%d)

# set working directory as pwd
WORKING_DIR=$(pwd)
OUTPUT_DIR="$WORKING_DIR/archive"

# Create the output directory if it does not exist
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
fi

# Run make all to generate the PDF, exit if it fails
echo "Running make all"
make all
if [ $? -ne 0 ]; then
    END_TIME=$(date +%s)
    echo "make all failed"
    echo "Unable to generate PDF. Exiting after $((END_TIME - START_TIME)) seconds"
    exit 1
fi


# If archived already today, delete the old archive
if [ -f "$OUTPUT_DIR/grammar-$DATE.pdf" ]; then
    rm -f "$OUTPUT_DIR/grammar-$DATE.pdf"
fi

# Move the generated PDF to the output directory
cp "$WORKING_DIR/grammar.pdf" "$OUTPUT_DIR/grammar-$DATE.pdf"


# Delete the auxiliary files
for EXT in $AUX_EXTS; do
    # Check if the file exists before deleting it, check other folders within the working directory as well
    find "$WORKING_DIR" -type f -name "*.$EXT" -delete
    echo "Deleting *.$EXT files"
done

# Move the generated PDF to the output directory
END_TIME=$(date +%s)
echo "Time taken: $((END_TIME - START_TIME)) seconds"

