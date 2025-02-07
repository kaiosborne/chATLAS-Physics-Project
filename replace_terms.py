import re
import json


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

    # Replace in order
    for pattern in patterns:
        replacement = compiled_glossary[pattern]
        text = pattern.sub(replacement, text)
    
    return text



# Import glossary
with open("acronyms.json", "r") as f:
    glossary = json.load(f)

# Import database create by get-mentions.py
with open("generated-data.json","r",encoding="utf-8") as f: # generated-data.json should be located in the same directory as this script, "r" means read only
    paper_data = json.load(f)

# Process the text in all mentions and replace abbreviations
for paper in paper_data:
    paper["mentions"] = [
        replace_term(mention, glossary) 
        for mention in paper["mentions"]
    ]

# Save result in another json
with open("processed_papers.json", "w") as f: # "w" means write mode
    json.dump(paper_data, f, indent=2)
