# Python script to generate the latex code for the vocabulary list

import os
import pandas as pd
import logging
import time

# Setup logging and format

# Delete the old log file
if os.path.exists("vocabulary/vocab-parser.log"):
    os.remove("vocabulary/vocab-parser.log")

# Create logger that writes to console and file simultaneously
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log to file
file_handler = logging.FileHandler("vocabulary/vocab-parser.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

start_time = time.time() 

# Path to the vocabulary file
vocab_file_path = "vocabulary/vocabulary.csv"

logger.info("Generating vocabulary file...")
logger.info(f"Reading vocabulary file: {vocab_file_path}")

# The vocabulary.csv file is a simple CSV file with three columns: word, part of speech, and English translation

# Read the vocabulary file
try:
    vocab_df = pd.read_csv(vocab_file_path, sep=';', encoding='utf-8')
except FileNotFoundError:
    logger.error(f"Error: File not found: {vocab_file_path}")
    logger.error("Please make sure that the vocabulary file exists in the vocabulary directory.")
    exit(1)
# Remove empty rows
vocab_df = vocab_df.dropna()
# Replace escaped umlauts with the actual umlauts for proper sorting, e.g. ä -> ä
logger.info("Replacing escaped umlauts...")

vocab_df['word'] = vocab_df['word'].str.replace(r'\\"a', 'ä')
vocab_df['word'] = vocab_df['word'].str.replace(r'\\"o', 'ö')
# Replace \ae{} with æ
vocab_df['word'] = vocab_df['word'].str.replace(r'\\ae\{\}', 'æ')

# Trim whitespace from the beginning and end of each column
vocab_df = vocab_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# remove duplicates based on the Niklorsk word
# removes only if duplicates have the same part of speech
logger.info("Removing duplicates...")
vocab_df = vocab_df.drop_duplicates(subset=['word', 'partofspeech'], keep='first')

# sort the vocabulary by the Niklorsk word
vocab_df = vocab_df.sort_values(by='word')

# Replace the csv file with the sorted and cleaned dataframe
# Delete the old vocabulary file
clean_vocab_file_path = "vocabulary/vocabulary_cleaned.csv"
if os.path.exists(clean_vocab_file_path):
    os.remove(clean_vocab_file_path)

pos_keys = {
    'adj': 'adjective',
    'adv': 'adverb',
    'art': 'article',
    'conj': 'conjunction',
    'interj': 'interjection',
    'nf': 'noun, feminine',
    'nm': 'noun, masculine',
    'nn': 'noun, neuter',
    'prep': 'preposition',
    'pron': 'pronoun',
    'v': 'verb'
}

clean_vocab_df = vocab_df
# Create new column "plural" taking the plural form of the word, which appears after a comma in the word column, e.g. "word, plural"
clean_vocab_df['plural'] = clean_vocab_df['word'].str.extract(r',\s*(.*)')
# Move plural column to second position, after the word column
clean_vocab_df = clean_vocab_df[['word', 'plural', 'partofspeech', 'translation']]
# Remove the comma and plural form from the word column using re module
clean_vocab_df['word'] = clean_vocab_df['word'].str.replace(r',\s*(.*)', '', regex=True)

# Replace the part of speech abbreviations with full names
clean_vocab_df['partofspeech'] = clean_vocab_df['partofspeech'].map(pos_keys)

# Save the cleaned vocabulary to a new file

clean_vocab_df.to_csv(clean_vocab_file_path, sep=';', encoding='utf-8', index=False)

logger.info("Created cleaned vocabulary file at vocabulary/vocabulary_cleaned.csv")



# Generate the latex code, skipping the first row which contains the column names
# \glossarypair{Niklorsk word}{part of speech}{English translation}
# Adds a \bigskip between letter groups by checking if the first letter of the current word is the same as the previous word
latex_code = ""
word_count = 0
prev_letter = ""


for index, row in vocab_df.iterrows():
    word = row['word']
    pos = row['partofspeech']
    translation = row['translation']


    # Add letter group heading for first word
    if word_count == 0:
        latex_code += f"\\vocabcentered{{{word[0].upper()}}}\n\n"

    # Check if the first letter of the current word is the same as the previous word, if not, add a \bigskip
    # Ignores the first word, as there is no previous word to compare
    if word_count > 0 and word[0] != prev_letter:
        latex_code += "\\bigskip\n"
        # Adds letter group heading
        latex_code += f"\\vocabcentered{{{word[0].upper()}}}\n\n"

    latex_code += f"\\glossarypair{{{word}}}{{{pos}}}{{{translation}}}\n"
    #new line
    latex_code += "\n"
    word_count += 1
    prev_letter = word[0]
    logger.info(f"[{word_count}] Added: {word}")



# Delete the old vocabulary file vocabulary/vocabulary.tex
if os.path.exists("vocabulary/vocabulary.tex"):
    os.remove("vocabulary/vocabulary.tex")

preface = """
% Path: vocabulary/vocabulary.tex
% This is an automatically generated file. Do not modify it directly. To update the vocabulary list, run the vocab-parser.py script.
% The vocabulary is sorted by the Niklorsk word
 
\chapter*{Vocabulary}
     
    """
# Add the part of speech abbreviations key as paragraph at the beginning of the vocabulary list
pos_key_as_string = ", ".join([f"{k} = {v}" for k, v in pos_keys.items()])
pos_key_print = f"{{\\small\\textbf{{Legend:}} {pos_key_as_string}}} \n\n"

preface += pos_key_print

# make two columns
preface += "\n\n"
preface += "\\begin{multicols}{2}\n\n \\footnotesize \n\n"

closing = "\\end{multicols}\n"


# Write the latex code to the vocabulary file
with open("vocabulary/vocabulary.tex", "w") as file:
    file.write(preface)
    file.write(latex_code)
    file.write(closing)

# Create one-line summary by part of speech
# group nn, nf, nm together as noun

pos_summary = vocab_df['partofspeech'].value_counts().to_dict()

nouns = ['nf', 'nn', 'nm']
pos_summary['noun'] = 0
pos_summary['noun'] += sum([pos_summary.pop(noun, 0) for noun in nouns])
pos_summary = {k: v for k, v in pos_summary.items() if k not in nouns}

# Sort dictionary by value, descending
pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1], reverse=True))

summary_str = ", ".join([f"{v} {k}" for k, v in pos_summary.items()])
logger.info(f"Summary by part of speech: {summary_str}")


end_time = time.time()
elapsed_time = end_time - start_time

logger.info(f"Vocabulary file generated successfully in {elapsed_time:.2f} seconds.")
logger.info(f"Total words in vocabulary: {word_count}.")
logger.info("Check vocabulary/vocabulary.tex for the generated vocabulary list.")
logger.info("Done.")