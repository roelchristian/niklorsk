# This is the makefile for the project.
# vocab - creates the vocabulary.tex file by running the vocab-parser.py script
# all - creates the pdf file

FILENAME := grammar


book:
	@echo "Creating the pdf file from the make menu"
	lualatex $(FILENAME).tex
	
	
# Create the vocabulary.tex file
vocab:
	@echo "Creating the vocabulary.tex file from the make menu"
	python3 vocab-parser.py


# Create the pdf file
all:
	@echo "Creating the pdf file and vocabulary from the make menu"
	python3 vocab-parser.py
	lualatex $(FILENAME).tex
	lualatex $(FILENAME).tex