import os
import json
from openai import OpenAI
from tqdm import tqdm
import re

# #define input and output directories
# dataDir = os.path.join("Data Scraping", "Test Outputs")
# outputDir = os.path.join("Data Scraping", "Test Outputs")  #temporary test file path

# # Convert to absolute paths if needed
# dataDir = os.path.abspath(dataDir)
# outputDir = os.path.abspath(outputDir)

# #set output file name
folderLocation = os.path.join("data scraping","Test Paper Data", "ATLASPapers","CDS_Record_2002197")
inputFilePath = os.path.join(folderLocation, "latex.txt")
outputFilePath = os.path.join(folderLocation, "output.json")


#export OPENAI_API_KEY="apikey" to set api key in environment

# def loadJSON(dataDir,fileName):
#     '''
#     Loads JSON file given file directory and filename.
#     Inputs:
#     dataDir - string, filepath of directory containing JSON.
#     fileName - string of filename.
#     Outputs:
#     data - 
#     '''
#     filePath = os.path.join(dataDir, fileName)
#     try:
    
#         with open(filePath, 'r') as file:
#             data = json.load(file)
#         print("JSON data loaded successfully!")
#     except FileNotFoundError:
#         print(f"Error: {fileName} was not found in", os.getcwd())
#         data = []  #set data to empty list if no file found
#     except json.JSONDecodeError as e:
#         print("Error decoding JSON:", e)
#         data = []
#     return data

def loadJSON(filePath):
    '''
    Loads JSON file given filepath.
    Inputs:
    filePath - string, filepath of the JSON file.
    Outputs:
    data - Parsed JSON data
    '''
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully!")
    except FileNotFoundError:
        print(f"Error: {filePath} was not found.")
        data = []  # Set data to empty list if no file found
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        data = []
    return data

# def saveJSON(data,outputDir,outputName):
#     '''
#     Saves JSON file to output directory.
#     Inputs:
#     data - data to save to JSON
#     outputDir - string of desired output directory
#     outputName - string of output JSON file name
#     Outputs:
#     JSON file of 'data' at outputDir/outputName
#     '''

#     outputJSON = json.dumps(data, indent=4)
#     outputPath = os.path.join(outputDir, outputName)

#     try:
#         with open(outputPath, 'w') as outputFile:
#             outputFile.write(outputJSON)
#     except Exception as e:
#         print("Error saving results:", e)

def saveJSON(data, outputPath):
    '''
    Saves JSON data to specified output file.
    Inputs:
    data - data to save to JSON
    outputPath - string of output file path
    Outputs:
    JSON file of 'data' at outputPath
    '''
    outputJSON = json.dumps(data, indent=4)

    try:
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputJSON)
        print("Output file saved successfully!")
    except Exception as e:
        print("Error saving results:", e)
        
        
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
    try:
        with open(fileLoc, encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file} was not found in {folderLoc}.")
        return []
    except UnicodeDecodeError as e:
        print(f"Error: Issue with file encoding: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []      

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

# Read lines and combine them into a JSON structure
lines = getLinesFromFile(folderLocation,'latex.txt')
if lines:
    try:
        content = ''.join(lines)  # Joining lines to create a full JSON string
        glossary = extract_abbreviation(content)

        results = []  # List to store processed entries
        #for entry in tqdm(content, desc="Processing entries", unit="entry"):
            # Ensure the required keys are present
            #if "abbreviations" in entry and "full_version" in entry:
                #abbrev = entry["abbreviations"]
                #full_version = entry["full_version"]
                
                # Generate glossary from the abbreviations
                #glossary = extract_abbreviation(" ".join(full_version))  # Assuming full_version is a list of strings
        definitions = get_definitions_from_glossary(glossary)

        results.append({
            "abbreviations": list(definitions.keys()),
            "definitions": list(definitions.values()) # Add definitions you obtained from get_definitions_from_glossary
                 })
    except Exception as e:
        print("An error occurred:", e)


print(results)

saveJSON(results,outputFilePath)

#find definition for each abbreviation in json and store result
#results = []




# for entry in tqdm(data, desc="Processing entries", unit="entry"):

#     abbrev = entry["abbreviations"] #set abbrevation to variable
#     full_version = entry["full_version"] 

#     definitions = []

#     for i in range(len(abbrev)):
#         definitions.append(get_definitions_from_glossary(abbrev[i], full_version[i]))

#     results.append({
#         "name": entry["name"], 
#         "mentions": entry["mentions"], 
#         "atlusUrl": entry["atlusUrl"], 
#         "paper": entry["paper"], 
#         "paperName": entry["paperName"],
#         "abbreviations": abbrev, 
#         "full_version": full_version,
#     })

#     saveJSON(results,outputFilePath)