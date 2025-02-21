import os
import re
import json
import logging
from collections import defaultdict
from openai import OpenAI
from tqdm import tqdm

client = OpenAI()


#pretty much all chat gpt and doesnt work - ignore this for now

# --------------------------
# Configuration & Directories
# --------------------------
logging.basicConfig(level=logging.INFO)

# Define input and output directories using relative paths
dataDir = os.path.abspath(os.path.join("Data Scraping", "Test Paper Data"))
outputDir = os.path.abspath(os.path.join("Data Scraping", "Test Outputs"))

# Ensure input directory exists
if not os.path.isdir(dataDir):
    print(f"Input directory not found: {dataDir}")
    exit(1)

# Create output directory if it does not exist
if not os.path.isdir(outputDir):
    print(f"Output directory not found, trying to create: {outputDir}")
    try:
        os.makedirs(outputDir)
    except OSError as error:
        print(f"Failed to create output directory: {error}")
        exit(1)

# --------------------------
# Regex Patterns & Identifiers
# --------------------------
# Patterns to detect figures, tables, table content, and math abbreviations.
figPattern = re.compile(r"[Ff]ig(?:\.|ure)?s? ?(\d+)")
tablePattern = re.compile(r"[Tt]able ?(\d+)")
tableContentPattern = re.compile(
    r"\\begin\{(?:table|tabular)\}[\s\S]*?\\end\{(?:table|tabular)\}", re.DOTALL
)
mathsPattern = re.compile(r"\\\((.*?)\\\)")

# Identifiers for naming
figIdentifier = "Figure "
tableIdentifier = "Table "
mathsIdentifier = ""  # No identifier needed; the math abbreviation is the captured content.

# File names for LaTeX and meta info
LATEX_FILE = "latex.txt"
META_FILE = "meta_info.txt"

# --------------------------
# Helper Functions
# --------------------------
def snipSentence(line, m):
    """
    Given a line and its regex match object, return the sentence containing that match.
    """
    sentenceBefore = line[:m.start()].split(". ")[-1]
    sentenceAfter = line[m.end():].split(". ")[0]
    return sentenceBefore + m.group(0) + sentenceAfter

def getLinesFromFile(folderLoc, filename):
    """
    Read all lines from a file located in a specified directory.
    """
    fileLoc = os.path.join(folderLoc, filename)
    with open(fileLoc, encoding="utf8") as f:
        return f.readlines()

def extractMentions(allLines, pattern, identifier, use_first_non_none_group=False):
    """
    Search through lines for a regex pattern and return a dictionary mapping
    (identifier + extracted match) to a list of sentences containing the match.
    
    Parameters:
    - allLines: List of lines (strings) to search.
    - pattern: The regex pattern to use.
    - identifier: A string to prepend to the extracted match.
    - use_first_non_none_group: If True, use the first non-None capturing group;
                                otherwise, use the entire match (group(0)).
    
    Returns:
    - A dictionary mapping (identifier + extracted match) to a list of mention strings.
    """
    mentions = defaultdict(list)
    for line in allLines:
        for m in re.finditer(pattern, line):
            if use_first_non_none_group:
                index = next((g for g in m.groups() if g is not None), m.group(0))
            else:
                index = m.group(0)
            mentions[identifier + index].append(snipSentence(line, m))
    return dict(mentions)

def extractPaperName(metaLinesList):
    """
    Extract the paper name from the meta info file.
    """
    paperNameLines = []
    capture = False
    for line in metaLinesList:
        if 'PAPER NAME :' in line:
            capture = True
            paperName = line.split('PAPER NAME :', 1)[1].strip()
            paperNameLines.append(paperName)
        elif 'LAST MODIFICATION DATE :' in line and capture:
            capture = False
            break
        elif capture:
            paperNameLines.append(line.strip())
    return ' '.join(paperNameLines) if paperNameLines else None

def get_definition_from_openai(abbrev, sentence):
    """
    Calls the OpenAI API to generate a definition for an abbreviation within a context sentence.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set in environment variables.")
        return None

    systemPrompt = (
        "You are a helpful assistant that is operating in a technical high energy physics context."
    )
    userPrompt = (
        f"Provide an extremely short definition (just one phrase) for the abbreviation '{abbrev}' "
        f"as used in the following context: {sentence}. Return only the definition without extra explanation. "
        "If you are unable to determine a definition with certainty, do not answer."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Change this if you use a different model.
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userPrompt},
            ],
            max_tokens=50,
            n=1,
            temperature=0.5,
        )
        # Extract the definition from the API response.
        definition = response.choices[0].message.content.strip()
        return definition
    except Exception as e:
        print(f"Error calling OpenAI API for '{abbrev}': {e}")
        return None

# --------------------------
# Main Processing Functions
# --------------------------
def process_latex_folders():
    """
    Process each subdirectory in dataDir to extract figure/table data and math abbreviations.
    Figures and tables are saved to a JSON file.
    
    Returns:
        math_abbreviations: A dictionary mapping math abbreviation to a list of mentions.
    """
    figures = []
    # Dictionary to aggregate math abbreviations (keys: abbreviation, values: list of mentions)
    math_abbreviations = {}

    for folder in os.listdir(dataDir):
        folderDir = os.path.join(dataDir, folder)
        if not os.path.isdir(folderDir):
            continue

        # Read LaTeX and meta info files; skip if missing.
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

        paperName = extractPaperName(metaLinesList)
        atlusUrl = max(metaLinesList[-1].split(), key=len)

        # Extract figures and tables using the first non-None captured group.
        figMentionDic = extractMentions(latexLinesList, figPattern, figIdentifier, use_first_non_none_group=True)
        tableMentionDic = extractMentions(latexLinesList, tablePattern, tableIdentifier, use_first_non_none_group=True)

        # Remove table environments from the LaTeX content.
        joinedLatex = '\n'.join(latexLinesList)
        cleanedJoinedLatex = re.sub(tableContentPattern, '', joinedLatex)
        cleanedLatexLinesList = cleanedJoinedLatex.splitlines()

        # Combine figure and table mentions.
        combinedMentionDic = {**figMentionDic, **tableMentionDic}

        # Extract math abbreviations using the full match.
        mathsMentionDic = extractMentions(cleanedLatexLinesList, mathsPattern, mathsIdentifier, use_first_non_none_group=False)

        # Aggregate math abbreviations across folders.
        for abbrev, mentions in mathsMentionDic.items():
            if abbrev in math_abbreviations:
                math_abbreviations[abbrev].extend(mentions)
            else:
                math_abbreviations[abbrev] = mentions

        # Compile data for figures/tables.
        for key, mentions in combinedMentionDic.items():
            # Clean mentions by removing any residual table environment content.
            cleanedMentions = [re.sub(tableContentPattern, '', m) for m in mentions]
            figures.append({
                "name": key,
                "mentions": cleanedMentions,
                "atlusUrl": atlusUrl,
                "paper": folder,
                "paperName": paperName
            })

    # Save the figures/tables data.
    outputFilePath = os.path.join(outputDir, "generated-data.json")
    try:
        with open(outputFilePath, "w", encoding="utf-8") as outfile:
            json.dump(figures, outfile, indent=4, ensure_ascii=False)
        print("Figure/table data saved to", outputFilePath)
    except Exception as e:
        print("Error saving figure/table data:", e)
    
    return math_abbreviations

def process_math_abbreviations(math_abbreviations):
    """
    For each math abbreviation extracted, call the OpenAI API to obtain a definition.
    Save the results to a JSON file.
    """
    results = []
    for abbrev, mentions in tqdm(math_abbreviations.items(), desc="Processing math abbreviations", unit="entry"):
        context = " ".join(mentions)
        definition = get_definition_from_openai(abbrev, context)
        results.append({
            "abbreviation": abbrev,
            "definition": definition,
            "mentions": mentions
        })

    output_path = os.path.join(outputDir, "abbreviation_definitions.json")
    try:
        with open(output_path, 'w', encoding="utf-8") as output_file:
            json.dump(results, output_file, indent=4)
        print("Abbreviation definitions saved to", output_path)
    except Exception as e:
        print("Error saving abbreviation definitions:", e)

# --------------------------
# Main Execution
# --------------------------
def main():
    math_abbreviations = process_latex_folders()
    process_math_abbreviations(math_abbreviations)

if __name__ == '__main__':
    main()