import json
import os

def transform_mentions(obj):
    """
    Transform the 'mentions' field in the given dictionary object into separate
    'mention' and 'caption' fields according to the following rules:

    1. If the 'mentions' field has only one element, use that single element for
       both 'mention' and 'caption'.
    2. If there are multiple elements, look for the first element containing a
       colon (":") and set it as 'caption'. The remaining elements become the
       'mention' field.
       - If no element contains a colon, use the last element as 'caption' and
         the rest as 'mention'.
    3. If, after removal of the caption element, only one mention remains, store
       it as a string (instead of a list with one element).
    4. Remove the original 'mentions' key from the object.

    Args:
        obj (dict): A dictionary that may contain a 'mentions' key (list of strings).

    Returns:
        dict: The same dictionary, but with new 'mention' and 'caption' fields
              replacing the original 'mentions' field.
    """
    
    # Process the "mentions" field if it exists.
    if "mentions" not in obj:
        return obj  # If not present, leave the object unchanged.
    
    mentions = obj["mentions"]
    del obj["mentions"]
    
    # Check if it's a valid non-empty list.
    if not isinstance(mentions, list) or not mentions:
        print(f"Warning: 'mentions' field is missing or empty in object: {obj.get('name', '')}")
        return obj
    
    # Apply transformation rules.
    if len(mentions) == 1:
        obj["mentions"] = []
        obj["caption"] = mentions[0]
    else:
        caption = None
        new_mentions = []
        # Find the first element that contains a colon.
        for m in mentions:
            if ":" in m and caption is None:
                caption = m
            else:
                new_mentions.append(m)
        # If no colon was found, use the last element as caption.
        if caption is None:
            caption = mentions[-1]
            new_mentions = mentions[:-1]
        # If only one element remains in mention, output it as a string.
        if len(new_mentions) == 1:
            new_mentions = new_mentions[0]
        obj["mentions"] = new_mentions
        obj["caption"] = caption
    
    # Remove the original "mentions" key.
    #del obj["mentions"]
    return obj

def transform_data(data):
    """
    Iterate over each object in the provided list and apply the 'transform_mentions'
    function to transform the 'mentions' field into separate 'mention' and 'caption'
    fields according to predefined rules.

    Args:
        data (list): A list of dictionaries, each of which may contain a 'mentions' key.

    Returns:
        list: A new list of dictionaries, each with 'mention' and 'caption' fields
              replacing the original 'mentions' field (if it existed).
    """
    
    # Process each object in the data array.
    transformed = []
    for obj in data:
        transformed_obj = transform_mentions(obj)
        transformed.append(transformed_obj)
    return transformed

def main():
    """
    Main function that processes the input JSON file and writes the transformed data
    to an output JSON file. Specifically, it reads 'DB.json', applies the 'transform_data'
    function (which splits the 'mentions' field into 'mention' and 'caption' fields), 
    and writes the result to 'DB_new.json'.
    """
    

    dataDir = os.path.join("Data Scraping", "Test Outputs")
    outputDir = os.path.join("Data Scraping", "Test Outputs")
    fileName = 'generated-data3.json'
    outputName = 'generated-data4.json'

    input_file =  os.path.join(dataDir, fileName)      # Your input file
    output_file = os.path.join(outputDir, outputName)  # Output file for the transformed data

    # Read the JSON data from DB1.json.
    with open(input_file, "r", encoding="utf-8") as infile:
        data = json.load(infile)
    
    # Transform the data.
    transformed_data = transform_data(data)
    
    # Write the transformed data to output.json.
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(transformed_data, outfile, indent=2)
    
    print(f"Transformation completed. Check the file: {output_file}")

if __name__ == "__main__":
    main()
