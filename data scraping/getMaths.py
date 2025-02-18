
import os
import re
import json
import logging
from collections import defaultdict



# Patterns to identify markdown maths inline and tables
mathsPattern = re.compile(r"\\\((.*?)\\\)")
tableContentPattern = re.compile(r"\\begin\{(?:table|tabular)\}[\s\S]*?\\end\{(?:table|tabular)\}", re.DOTALL)

# Identifiers to prepend to the figure and table numbers for naming
mathsIdentifier = ""

# Constant filenames
LATEX_FILE = "latex.txt"
META_FILE = "meta_info.txt"

def snipSentence(line,m):
    """

    Given a paragraph and its match object return the sentence containing that match

    Inputs:
    - line: The line that the match is in
    - m: The match object

    Returns:
    - A sentence
    """
    sentenceBefore = line[:m.start()].split(". ")[-1]
    sentenceAfter = line[m.end():].split(". ")[0]
    return sentenceBefore + m.group(0) + sentenceAfter

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
        lines = f.readlines()
    if not lines:
        logging.warning(f"File {file} is empty.")
    return lines
    
def extractAbbreviationsAndMentions(allLines, pattern, identifier):
    """
    Search through a list of lines for mentions of images (figures/tables) based on provided pattern, then group and label them.
    
    Parameters:
    - allLines: List of strings to search through.
    - pattern: Regex pattern to identify image mentions.
    - identifier: String to prepend to image numbers for naming.
    
    Returns:
    - A dictionary mapping image names to lists of lines in which they are mentioned.
    """
    mentions = defaultdict(list)
    for line in allLines:
        # For all lines iterate through all match objects found in the line
        for m in re.finditer(pattern,line):
            index = m.group(0)
            # If the line is figurelike then add to captions and add placeholder in mentions, else add to mentions#
            mentions[identifier + index].append(snipSentence(line,m))
    return dict(mentions)

# Define input and output directories using relative paths
dataDir = os.path.join("Data Scraping", "Test Paper Data") 
outputDir = os.path.join("Data Scraping", "Test Paper Data")  # temporary test file path (remove Test later)

# Convert to absolute paths if needed
dataDir = os.path.abspath(dataDir)
outputDir = os.path.abspath(outputDir)   

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

abbreviations = []
# Process each subdirectory in the input directory
for f in os.listdir(dataDir):
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

    joinedLatex = '\n'.join(latexLinesList)
    cleanedJoinedLatex = re.sub(tableContentPattern, '', joinedLatex)
    cleanedLatexLinesList = cleanedJoinedLatex.splitlines()

    mathsMentionDic = extractAbbreviationsAndMentions(cleanedLatexLinesList, mathsPattern, mathsIdentifier)


    for key, mentions in mathsMentionDic.items():

        abbreviations.append({
            "name": key, 
            "mentions": mentions, 
        })

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, "generated-data-maths.json")

# Write the compiled data to the output JSON file
with open(outputFilePath, "w",encoding="utf-8") as outfile:
    json.dump(abbreviations, outfile, indent=4, ensure_ascii=False)
