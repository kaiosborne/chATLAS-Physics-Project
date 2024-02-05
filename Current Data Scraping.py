#%%
import os
import re
import json
import logging
from collections import defaultdict

# Patterns to identify figure and table references in the text files, precompiled for performance
figPattern = re.compile(r"[Ff]ig. (\d+)|[Ff]igures* (\d+)")
tablePattern = re.compile(r"[Tt]able (\d+)")

# Identifiers to prepend to the figure and table numbers for naming
figIdentifier = "Figure "
tableIdentifier = "Table "

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

def extractImageNamesAndMentions(allLines, pattern, identifier):
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
        match = pattern.search(line)
        if match:
            # Extract the first non-None group match
            image_number = next(g for g in match.groups() if g is not None)
            mentions[identifier + image_number].append(line)
    return dict(mentions)

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

def extractFigureCaptionsAndMentions(filePath):
    """
    Extracts figure captions and paragraphs containing mentions of figures from a given text file.
    
    Parameters:
    - filePath: Path to the text file.
    
    Returns:
    - A tuple of two dictionaries: 
        - First dict: Captions with figure numbers as keys.
        - Second dict: Paragraphs mentioning figures with figure numbers as keys.
    """
    figure_caption_pattern = r'^Figure (\d+):'
    figure_paragraph_pattern = r'(Figure|Fig|figure|fig)\s+(\d+)[^\n:]*'
    paragraph_pattern = r'((?:\n|^)(?:(?!\n\n).)+)'
    figures = {}
    paragraphs = {}
    
    try:
        with open(filePath, 'r') as file:
            content = file.read()
            # Extract figures and captions
            for line in content.split('\n'):
                if re.match(figure_caption_pattern, line, re.IGNORECASE):
                    figure_number = re.search(figure_caption_pattern, line, re.IGNORECASE).group(1)
                    figures[f'Figure {figure_number}'] = line.strip()
            
            # Extract paragraphs containing figure mentions
            for paragraph_match in re.finditer(paragraph_pattern, content, re.DOTALL):
                paragraph = paragraph_match.group(1).strip()
                fig_matches = re.finditer(figure_paragraph_pattern, paragraph)
                for fig_match in fig_matches:
                    fig_number = fig_match.group(2)
                    if fig_number not in paragraphs and not re.match(figure_caption_pattern, paragraph):
                        paragraphs[f'Figure {fig_number}'] = paragraph

    except FileNotFoundError:
        print(f"The file {filePath} was not found.")
        return {}, {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}, {}

    return figures, paragraphs

# Define input and output directories
dataDir = "/Users/georgedoumenis-ramos/Documents/ATLASPublications"
outputDir = "/Users/georgedoumenis-ramos/Documents/OUTPUT DATA"

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

    # Extract captions and mentions for figures
    figureCaptions, figureMentions = extractFigureCaptionsAndMentions(os.path.join(folderDir, LATEX_FILE))

    # Extract mentions of figures and tables from the latex file
    figMentionDic = extractImageNamesAndMentions(latexLinesList, figPattern, figIdentifier)
    tableMentionDic = extractImageNamesAndMentions(latexLinesList, tablePattern, tableIdentifier)

    # Combine figure and table mentions into a single dictionary
    combinedMentionDic = {**figMentionDic, **tableMentionDic}

    # Compile the data for each figure/table into a list of dictionaries
    for key, mentions in combinedMentionDic.items():
        figures.append({
            "name": key, 
            "mentions": mentions, 
            "caption": figureCaptions.get(key, ""),  # Include the extracted figure caption
            "atlusUrl": atlusUrl, 
            "paper": f, 
            "paperName": paperName  # Include the extracted paper name here
        })

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, "generated-data.json")

# Write the compiled data to the output JSON file
with open(outputFilePath, "w") as outfile:
    json.dump(figures, outfile, indent=4, ensure_ascii=False)

