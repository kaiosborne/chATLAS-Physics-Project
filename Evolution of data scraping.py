# %%
##The following is the regular version
# %%
import os
import re
import json
import itertools

# Patterns to identify figure and table references in the text files
figPatterns = [r"[Ff]ig. (\d+)", r"[Ff]igures* (\d+)"]
tablePatterns = [r"[Tt]able (\d+)"]

# Identifiers to prepend to the figure and table numbers for naming
figIdentifier = "Figure "
tableIdentifier = "Table "


def getLinesFromFile(folderLoc, file):
    """
    Read all lines from a file located in a specified directory.

    Inputs:
    - folderLoc: Path of the directory containing the file.
    - file: Name of the file to read.

    Outputs:
    - A list of lines from the file.
    """
    fileLoc = os.path.join(folderLoc, file)
    with open(fileLoc, encoding="utf8") as f:
        return f.readlines()


def extractImageNamesAndMentions(allLines, patterns, identifier):
    """
    Search through a list of lines for mentions of images (figures/tables) based on provided patterns, then group and label them.

    Inputs:
    - allLines: List of strings  to search through.
    - patterns: List of regex patterns to identify image mentions.
    - identifier: String to prepend to image numbers for naming.

    Outputs:
    - A dictionary mapping image names to lists of lines in which they are mentioned.
    """
    unsortedMentions = []
    for line in allLines:
        for p in patterns:
            if re.search(p, line):
                search = re.search(p, line)
                unsortedMentions.append({"image number": search.group(1), "line": line})
    # Group the mentions by image number and convert the line information from dictionaries to strings
    mentions = {identifier + imageNum: list(imageDics) for imageNum, imageDics in
                itertools.groupby(unsortedMentions, key=lambda x: x["image number"])}
    return {k: [l["line"] for l in v] for k, v in mentions.items()}


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
        latexLinesList = getLinesFromFile(folderDir, file="latex.txt")
    except FileNotFoundError:
        print(f"latex.txt not found in: {folderDir}")
        continue

    try:
        metaLinesList = getLinesFromFile(folderDir, file="meta_info.txt")
    except FileNotFoundError:
        print(f"meta_info.txt not found in: {folderDir}")
        continue

    # Extract the URL from the last line of the metadata file
    atlusUrl = max(metaLinesList[-1].split(), key=len)

    # Extract mentions of figures and tables from the latex file
    figMentionDic = extractImageNamesAndMentions(latexLinesList, figPatterns, figIdentifier)
    tableMentionDic = extractImageNamesAndMentions(latexLinesList, tablePatterns, tableIdentifier)

    # Combine figure and table mentions into a single dictionary
    combinedMentionDic = {**figMentionDic, **tableMentionDic}

    # Compile the data for each figure/table into a list of dictionaries
    for key, mentions in combinedMentionDic.items():
        figures.append({"name": key, "mentions": mentions, "atlusUrl": atlusUrl, "paper": f})

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, "generated-data.json")

# Write the compiled data to the output JSON file
with open(outputFilePath, "w") as outfile:
    json.dump(figures, outfile, indent=4)

# %%
# The following code adds a few changes namely :
#
# -Added some basic docstrings
#
# -Added comments
#
# -Added some error checking
#
# -Some performance improvement (using re.compile although not very important)
#
# -Errors now handled by logging rather than printing
#
# -If directory not found, continues processing, rather than simply stopping
#
# -Replaced the itertools.groupby with defaultdict(list), did some research and is apparently more robust a function to use.
#
# -Add what file isn’t found  when catching and reporting the errors
#
# -After making JSON, set ensure_ascii = False to ensure we maintain the original characters.
# %%
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

    # Extract the URL from the last line of the metadata file
    atlusUrl = max(metaLinesList[-1].split(), key=len)

    # Extract mentions of figures and tables from the latex file
    figMentionDic = extractImageNamesAndMentions(latexLinesList, figPattern, figIdentifier)
    tableMentionDic = extractImageNamesAndMentions(latexLinesList, tablePattern, tableIdentifier)

    # Combine figure and table mentions into a single dictionary
    combinedMentionDic = {**figMentionDic, **tableMentionDic}

    # Compile the data for each figure/table into a list of dictionaries
    for key, mentions in combinedMentionDic.items():
        figures.append({"name": key, "mentions": mentions, "atlusUrl": atlusUrl, "paper": f})

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, "generated-data.json")

# Write the compiled data to the output JSON file
with open(outputFilePath, "w") as outfile:
    json.dump(figures, outfile, indent=4, ensure_ascii=False)

# %%
# In the following code I proceed to create and test a function that will make a file of all of the paper names to make sure that can be done first.
# %%
import os


def extractPaperName(metaLinesList):
    """
    Extracts the paper name from the meta info file.

    Parameters:
    - metaLinesList: List of strings, each representing a line from the meta_info.txt file.

    Returns:
    - The paper name as a string. Returns None if the paper name can't be found.
    """
    paperName = None
    for line in metaLinesList:
        if 'PAPER NAME :' in line:
            paperName = line.split('PAPER NAME :', 1)[1].strip()
        elif 'LAST MODIFICATION DATE :' in line and paperName:
            # Return the paper name once we reach the last modification date line
            return paperName
    return paperName  # Return whatever we've got as the paper name


def getLinesFromFile(filePath):
    """
    Read all lines from a file.

    Parameters:
    - filePath: Path of the file to read.

    Returns:
    - A list of lines from the file.
    """
    try:
        with open(filePath, encoding="utf8") as f:
            return f.readlines()
    except Exception as e:
        print(f"Error reading file {filePath}: {e}")
        return []


def extractAndSavePaperNames(dataDir, outputFilePath):
    """
    Extracts paper names from each meta_info.txt in the subdirectories of the given data directory
    and saves them to a text file.

    Parameters:
    - dataDir: Directory containing subdirectories with meta_info.txt files.
    - outputFilePath: File path where the list of paper names will be saved.
    """
    paperNames = []

    for folder in os.listdir(dataDir):
        folderDir = os.path.join(dataDir, folder)

        # Skip if 'folder' is not a directory
        if not os.path.isdir(folderDir):
            print(f"Skipping {folder}, since it's not a directory.")
            continue

        metaFilePath = os.path.join(folderDir, "meta_info.txt")

        # Skip if meta_info.txt does not exist in the folder
        if not os.path.isfile(metaFilePath):
            print(f"meta_info.txt not found in {folderDir}")
            continue

        # Read meta_info.txt and extract the paper name
        metaLines = getLinesFromFile(metaFilePath)
        paperName = extractPaperName(metaLines)
        if paperName:
            paperNames.append(paperName)
        else:
            print(f"Paper name not found in {metaFilePath}")

    # Save the list of paper names to the output file
    try:
        with open(outputFilePath, 'w', encoding="utf8") as outFile:
            for name in paperNames:
                outFile.write(name + '\n')
        print(f"Paper names successfully saved to {outputFilePath}")
    except Exception as e:
        print(f"Error writing to file {outputFilePath}: {e}")


# Usage example:
dataDir = "/Users/georgedoumenis-ramos/Documents/ATLASPublications"
outputFilePath = "/Users/georgedoumenis-ramos/Documents/paper_names.txt"
extractAndSavePaperNames(dataDir, outputFilePath)

# %% md
# The following code adds the name of each paper to each figure, in the file.
# %%
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
            "atlusUrl": atlusUrl,
            "paper": f,
            "paperName": paperName  # Include the extracted paper name here
        })

# Define the path for the output JSON file
outputFilePath = os.path.join(outputDir, "generated-data.json")

# Write the compiled data to the output JSON file
with open(outputFilePath, "w") as outfile:
    json.dump(figures, outfile, indent=4, ensure_ascii=False)

# %%
# The following addition adds the captions by searching the text files for them.
# %%
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

