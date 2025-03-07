#%%
import os
import re
import json
import logging
from collections import defaultdict

# Patterns to identify figure and table references in the text files, precompiled for performance
figPattern = re.compile(r"[Ff]ig. (\d+)(\.\d+)?|[Ff]igures* (\d+)(\.\d+)?")
tablePattern = re.compile(r"[Tt]able (\d+)")

# Identifiers to prepend to the figure and table numbers for naming
figIdentifier = "Figure "
tableIdentifier = "Table "

# Constant filenames
LATEX_FILE = "latex.txt"
META_FILE = "meta_info.txt"


def snipSentence(line,m):
    """

    Given a pagraph and its match object return the senctence containing that match

    Inputs:
    - line: The line that the match is in
    - m: The match object

    Returns:
    - A sentence
    """
    sentenceBefore = line[:m.start()].split(". ")[-1]
    sentenceAfter = line[m.end():].split(". ")[0]
    return sentenceBefore + m.group(0) + sentenceAfter 


def labelByIterator(dDict,m,identifier,line):
    """ 

    Given a dictionary and mention object add mention to dictionary with the appropriate key.

    Parameters:
    - dDict: Dictionary that is being added to
    - m: Match object
    - identifier: Identifer used in the dictionaries key name
    - line: line where the match is located

    Returns:
    - Updated dictionary
    """
    groupIterator = iter(g for g in m.groups() if g is not None)
    index1 = next(groupIterator) 
    try:
        index2 = next(groupIterator)
        dDict[identifier + index1+index2].append(line)
    except:
        dDict[identifier + index1].append(line)
    return dDict

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

def extractImageNamesAndMentions(allLines, pattern, identifier):
    """
    Search through a list of lines for mentions of images (figures/tables) based on provided pattern, 
    then sort into figures and mentions and return both dictionaries.
    
    Parameters:
    - allLines: List of strings to search through.
    - pattern: Regex pattern to identify image mentions.
    - identifier: String to prepend to image numbers for naming.
    
    Returns:
    - A dictionary mapping image names to lists of lines in which they are mentioned (excluding figure like).
    - A dictionary mapping image names to lists of figure like mentions.
    """
    captions, mentions = defaultdict(list), defaultdict(list)
    for line in allLines:
        # For all lines iterate through all match objects found in the line
        for m in re.finditer(pattern,line):
            # If the line is figurelike then add to captions and add placeholder in mentions, else add to mentions
            if m.start() == 0:
                captions = labelByIterator(captions,m,identifier,line)
                mentions = labelByIterator(mentions,m,identifier,"")
            else:
                mentions = labelByIterator(mentions,m,identifier,snipSentence(line,m))
    return dict(mentions), dict(captions)

def extractPaperName(metaLinesList):
    """
    Extracts the paper name from the meta info file.
    
    Parameters:
    - metaLinesList: List of strings, each representing a line from the meta_info.txt file.
    
    Returns:
    - The paper name as a string. Returns None if the paper name can't be found.
    """
    paperNameLines = []
    capture = False
    for line in metaLinesList:
        if 'PAPER NAME :' in line:
            capture = True
            paperName = line.split('PAPER NAME :', 1)[1].strip()
            paperNameLines.append(paperName)  # Capture the rest of the line after 'PAPER NAME :'
        elif 'LAST MODIFICATION DATE :' in line and capture:
            # Stop capturing after 'LAST MODIFICATION DATE :'
            capture = False
            break
        elif capture:
            # If we are in capture mode, append lines to paperNameLines
            paperNameLines.append(line.strip())
    
    return ' '.join(paperNameLines) if paperNameLines else None


# Define input and output directories
dataDir = "C:\workspace\data-for-project"
outputDir = "C:\workspace\git-repos\physics-project"

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

figures = []
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

    # Extract the paper name from the metadata file
    paperName = extractPaperName(metaLinesList)
    
    # Extract the URL from the last line of the metadata file
    atlusUrl = max(metaLinesList[-1].split(), key=len)

    # Extract mentions and captions of figures and tables from the latex file
    figMentionDic, figCaptionDic = extractImageNamesAndMentions(latexLinesList, figPattern, figIdentifier)
    tableMentionDic,tableCaptionDic = extractImageNamesAndMentions(latexLinesList, tablePattern, tableIdentifier)

    # Combine figure and table mentions into a single dictionary
    combinedMentionDic = {**figMentionDic, **tableMentionDic}
    combinedCaptionDic = {**figCaptionDic, **tableCaptionDic}

    for key, mentions in combinedMentionDic.items():
        # Try to find the caption
        try:
            captions = combinedCaptionDic[key]
        except:
            captions = "caption not found"
        
        # Remove all "" mentions
        mentions = [m for m in mentions if m != ""]

        # Append this figures caption
        figures.append({
            "name": key,
            "captions": captions, 
            "mentions": mentions, 
            "atlusUrl": atlusUrl, 
            "paper": f, 
            "paperName": paperName  # Include the extracted paper name here
        })

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, "generated-data.json")

# Write the compiled data to the output JSON file
with open(outputFilePath, "w",encoding="utf-8") as outfile:
    json.dump(figures, outfile, indent=4, ensure_ascii=False)

