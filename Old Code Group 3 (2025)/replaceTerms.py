import re
import json
import os 


# Create a function to replace terms to complete forms
def replace_term(text,glossary):
    """
    replace acronyms terms to complete forms
    """
    # Build a dictionary of compiled regular expressions
    compiled_glossary = {
        re.compile(r'\b' + re.escape(k) + r'\b', re.IGNORECASE): v
        for k, v in glossary.items()
    }

    # Sort by length in descending order
    patterns = sorted(compiled_glossary.keys(), key=lambda pat: len(pat.pattern), reverse=True)

    replacement = None
    
    # Replace in order
    for pattern in patterns:
        replacement = compiled_glossary[pattern]
        text = pattern.sub(replacement, text)

    if replacement:
        return f"{replacement} ({text})"
    
    else:
        return text


# Import jsons with relative path
# Import glossary 
#with open("acronyms.json", "r") as f:
    #glossary = json.load(f)
# Import database create by get-mentions.py

dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")

fileName = 'generated-data.json'
outputName = 'generated-data-replaced.json'

filePath = os.path.join(dataDir, fileName)
outputPath = os.path.join(outputDir, outputName)


with open(filePath,"r",encoding="utf-8") as f: # generated-data.json should be located in the same directory as this script, "r" means read only
    paper_data = json.load(f)


# Import jsons with absolute path
#glossary_path = r"C:\Users\ "
#paper_data_path = r"C:\Users\ "
#output_path = r"C:\Users\ "
# Load JSON files
#glossary = json.load(glossary_path)
#paper_data =  json.load(paper_data_path)

# Process the text in all mentions and replace abbreviations
for paper in paper_data:
    glossary = dict(zip(paper["abbrevs"], paper["abbrevDefinitions"]))
    paper["mentions"] = [
        replace_term(mention, glossary) 
        for mention in paper["mentions"]
    ]

# Save result in another json
with open(outputPath, "w") as f: # "w" means write mode
    json.dump(paper_data, f, indent=2)
