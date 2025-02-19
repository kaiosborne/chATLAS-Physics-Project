import json
import re

def apply_glossary(text, glossary):
    """
    Replace abbreviations in a string with the format:
        LSP -> LSP(Luminosity Signal Process)
    If a glossary value is a list, it is joined into a single string.
    """
    if not isinstance(text, str):
        return text
    
    for abbr, full in glossary.items():
        # If 'full' is a list, join its elements into a string.
        if isinstance(full, list):
            joined = ", ".join(full)
        else:
            joined = full
        
        # We create a replacement of the form 'abbr(full)'
        # e.g. 'LSP(Luminosity Signal Process)'
        replacement = f"{abbr}({joined})"
        
        # Use lookbehind/lookahead to allow punctuation, parentheses, etc. after 'abbr'
        pattern = rf'(?<!\w){re.escape(abbr)}(?!\w)'
        text = re.sub(pattern, replacement, text)
    
    return text

def process_field(field, glossary):
    """
    Recursively apply glossary replacements to strings and lists of strings.
    """
    if isinstance(field, str):
        return apply_glossary(field, glossary)
    elif isinstance(field, list):
        return [process_field(item, glossary) for item in field]
    else:
        return field

def main():
    input_file = "DB1.json"          # Input file name
    glossary_file = "glossary.json"  # Glossary file
    output_file = "output.json"      # Output file name

    # Load the glossary from glossary.json.
    with open(glossary_file, "r", encoding="utf-8") as gf:
        glossary = json.load(gf)
    
    # If the loaded glossary is a list, extract the first element
    # so 'glossary' becomes a dict, not a list with one dict inside.
    if isinstance(glossary, list) and len(glossary) > 0:
        glossary = glossary[0]
    
    # Load data from DB_new.json.
    with open(input_file, "r", encoding="utf-8") as infile:
        data = json.load(infile)
    
    # Process each object's "mention" and "caption" fields.
    for obj in data:
        if "mention" in obj:
            obj["mention"] = process_field(obj["mention"], glossary)
        if "caption" in obj:
            obj["caption"] = process_field(obj["caption"], glossary)
    
    # Write the transformed data to output.json.
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)
    
    print(f"Transformation completed. Check the file: {output_file}")

if __name__ == "__main__":
    main()
