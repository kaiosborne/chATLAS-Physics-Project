import os
import re
import json
import logging
from collections import defaultdict
from tqdm import tqdm

# Define input and output directories using relative paths
dataDir = os.path.join("Data Scraping", "Test Paper Data","ATLASPapers") 
outputDir = os.path.join("Data Scraping", "Test Outputs")  # temporary test file path (remove Test later)

# Convert to absolute paths if needed
dataDir = os.path.abspath(dataDir)
outputDir = os.path.abspath(outputDir)

#set output file name
outputName = "generated-data.json"

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

# Patterns to identify figure and table references in the text files, precompiled for performance
figPattern = re.compile(r"[Ff]ig. (\d+)|[Ff]igures* (\d+)")
tablePattern = re.compile(r"[Tt]able (\d+)")
mathsPattern = re.compile(r"(\\\(.*?\\\))")
tableContentPattern = re.compile(r"\\begin\{(?:table|tabular)\}[\s\S]*?\\end\{(?:table|tabular)\}", re.DOTALL)

# Identifiers to prepend to the figure and table numbers for naming
figIdentifier = "Figure "
tableIdentifier = "Table "
mathsIdentifier = ""

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

def extractPatternAndMentions(allLines, pattern, identifier):
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
            index = next(g for g in m.groups() if g is not None)
            # If the line is figurelike then add to captions and add placeholder in mentions, else add to mentions#
            mentions[identifier + index].append(snipSentence(line,m))
    return dict(mentions)

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


# Process each subdirectory in the input directory
for f in tqdm(os.listdir(dataDir), desc="Processing directories", unit="dir"):
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

    # Extract mentions of figures and tables from the latex file
    figMentionDic = extractPatternAndMentions(latexLinesList, figPattern, figIdentifier)
    tableMentionDic = extractPatternAndMentions(latexLinesList, tablePattern, tableIdentifier)

    #remove tables from data before maths detection
    joinedLatex = '\n'.join(latexLinesList)

    cleanedJoinedLatex = re.sub(tableContentPattern, '', joinedLatex)
    cleanedLatexLinesList = cleanedJoinedLatex.splitlines()

    abbrevAllMentionDic = extract_abbreviation(cleanedJoinedLatex)

    mathsAllMentionDic = extractPatternAndMentions(cleanedLatexLinesList, mathsPattern, mathsIdentifier)

    # Combine figure and table mentions into a single dictionary
    combinedMentionDic = {**figMentionDic, **tableMentionDic}

    # Compile the data for each figure/table into a list of dictionaries
    figures = []
    for key, mentions in combinedMentionDic.items():

        cleanedMentionsList = []

        allAbbrevTermsPresent = {}
        allMathsTermsPresent = {}

        for m in mentions:
            cleanedMention = re.sub(tableContentPattern, '', m) #remove instances of tables from saved mentions
            cleanedMentionsList.append(cleanedMention)
            #keeps maths terms and abbreviations that are present in current loop cleaned mentions (ignore terms in rest of paper)
            
            mathsTermsPresent = {
                key: item
                for key, item in mathsAllMentionDic.items()
                if key in cleanedMention
            }
            
            #cleaning maths from mention before abbrev checking
            cleanedMentionNoMaths = re.sub(r'\\\(.*?\\\)', '', cleanedMention)

            abbrevTermsPresent = {
                key: item
                for key, item in abbrevAllMentionDic.items()
                if key in cleanedMentionNoMaths
            }

            allAbbrevTermsPresent.update(abbrevTermsPresent) #adds terms present in current mention in loop to overall present
            allMathsTermsPresent.update(mathsTermsPresent)

        abbrevDefinitions = get_definitions_from_glossary(allAbbrevTermsPresent) #find definitions of abbrev

        figures.append({
            "name": key, 
            "mentions": cleanedMentionsList, 
            "atlusUrl": atlusUrl, 
            "paper": f, 
            "paperName": paperName,
            "abbrevs": list(abbrevDefinitions.keys()),
            "abbrevDefinitions": list(abbrevDefinitions.values()),
            "maths": list(allMathsTermsPresent.keys()), 
            "mathsContext": list([value[0] for value in allMathsTermsPresent.values()]),
        })

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, outputName)

# Write the compiled data to the output JSON file
with open(outputFilePath, "w",encoding="utf-8") as outfile:
    json.dump(figures, outfile, indent=4, ensure_ascii=False)