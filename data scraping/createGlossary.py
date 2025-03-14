import os
import re
import json
import logging
from collections import defaultdict
from tqdm import tqdm

# Define input and output directories using relative paths
dataDir = os.path.join("Data Scraping", "Test Paper Data","CDS_doc") 
outputDir = os.path.join("Data Scraping", "Test Outputs")  # temporary test file path (remove Test later)

# Convert to absolute paths if needed
dataDir = os.path.abspath(dataDir)
outputDir = os.path.abspath(outputDir)

#set output file name
outputName = "glossaryCDS_doc.json"

#Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, outputName)

# Check if the input directory exists, exit if not
if not os.path.isdir(dataDir):
    print(f"Input directory not found: {dataDir}")
    exit(1)

# Check if the output directory exists, create it if not
if not os.path.isdir(outputDir):
    print(f"Output directory not found, trying to create: {outputDir}")
    try:
        os.makedirs(outputDir)
    except OSError as error:
        print(f"Failed to create output directory: {error}")
        exit(1)

# Constant filenames
LATEX_FILE = "latex.txt"
META_FILE = "meta_info.txt"

def getLinesFromFile(folderLoc, file):
    """
    Read all lines from a file located in a specified directory.
    
    Parameters:
    - folderLoc: Path of the directory containing the file.
    - file: Name of the file to read.
    
    Returns:
    - A list of lines from the file.
    """
    fileLoc = os.path.join(folderLoc, file)
    with open(fileLoc, encoding="utf8") as f:
        return f.readlines()

def extract_abbreviation(text):
    abbreviation_pattern = r'([A-Za-z\s-]+)\s*[\[\d+\]]*\s+\(\b([A-Z][A-Za-z]*)\)'

    abbreviations = re.findall(abbreviation_pattern, text)

    glossary = {}

    for meaning, abbr in abbreviations:
        glossary[abbr] = meaning.strip()

    return glossary

def find_best_long_form(short_form, long_form):
    #glossary = long_form
    #short_form = glossary.items
    s_index = len(short_form) - 1  # Set s_index at the end of the short form
    l_index = len(long_form) - 1    # Set l_index at the end of the long form

    while s_index >= 0:  # Scan the short form starting from end to start
        curr_char = short_form[s_index].lower()  # Get the current character to match (ignore case)

        # Ignore non-alphanumeric characters
        if not curr_char.isalnum():
            s_index -= 1
            continue

        # Decrease l_index while the current character in the long form
        # does not match the current character in the short form.
        while (l_index >= 0 and long_form[l_index].lower() != curr_char) or \
              (s_index == 0 and l_index > 0 and long_form[l_index - 1].isalnum()):
            l_index -= 1

        # If no match was found in the long form for the current character, return None (no match).
        if l_index < 0:
            return None

        # A match was found for the current character. Move to the next character in the long form.
        l_index -= 1
        s_index -= 1
    
    # Find the beginning of the first word (in case the first character matches the beginning of a hyphenated word).
    l_index = long_form.rfind(' ', 0, l_index + 1) + 1
    
    # Return the best long form, the substring of the original long form, starting from l_index up to the end.
    return long_form[l_index:]

def get_definitions_from_glossary(glossary):
    definitions = {}
    
    for abbr, meaning in glossary.items():

        best_long_form = find_best_long_form(abbr, meaning)
        definitions[abbr] = best_long_form if best_long_form else meaning  # Use best long form or original meaning if not found
    
    return definitions

allAbbrevDefinitions = {}

# Process each subdirectory in the input directory
for f in tqdm(os.listdir(dataDir), desc="Finding abbrevations", unit="dir"):
    folderDir = os.path.join(dataDir, f)
    # Skip if 'f' is not a directory
    if not os.path.isdir(folderDir):
        continue
    # Attempt to read the latex and metadata files, skip the folder if either file is missing
    try:
        latexLinesList = getLinesFromFile(folderDir, LATEX_FILE)
    except FileNotFoundError:
        logging.error(f"{LATEX_FILE} not found in: {folderDir}")
        continue
    try:
        metaLinesList = getLinesFromFile(folderDir, META_FILE)
    except FileNotFoundError:
        logging.error(f"{META_FILE} not found in: {folderDir}")
        continue


    #remove tables from data before abbreviation detection
    joinedLatex = '\n'.join(latexLinesList)
    tableContentPattern = re.compile(r"\\begin\{(?:table|tabular)\}[\s\S]*?\\end\{(?:table|tabular)\}", re.DOTALL)
    cleanedJoinedLatex = re.sub(tableContentPattern, '', joinedLatex)

    terminationPattern = re.compile(r"(Acknowledgements|References).*", re.DOTALL | re.IGNORECASE)

    #delete everything after acknowledgements or references headers
    
    cleanedJoinedLatex = re.sub(terminationPattern, '', cleanedJoinedLatex)

    abbrevAllMentionDic = extract_abbreviation(cleanedJoinedLatex)

    abbrevDefinitions = get_definitions_from_glossary(abbrevAllMentionDic) #find definitions of abbrev

    allAbbrevDefinitions.update(abbrevDefinitions)

# Write the compiled data to the output JSON file
with open(outputFilePath, "w",encoding="utf-8") as outfile:
    json.dump(allAbbrevDefinitions, outfile, indent=4, ensure_ascii=False)