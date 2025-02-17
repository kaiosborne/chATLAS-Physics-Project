import json

def transform_mentions(obj):
    # Process the "mentions" field if it exists.
    if "mentions" not in obj:
        return obj  # If not present, leave the object unchanged.
    
    mentions = obj["mentions"]
    
    # Check if it's a valid non-empty list.
    if not isinstance(mentions, list) or not mentions:
        print(f"Warning: 'mentions' field is missing or empty in object: {obj.get('name', '')}")
        return obj
    
    # Apply transformation rules.
    if len(mentions) == 1:
        obj["mention"] = mentions[0]
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
        obj["mention"] = new_mentions
        obj["caption"] = caption
    
    # Remove the original "mentions" key.
    del obj["mentions"]
    return obj

def transform_data(data):
    # Process each object in the data array.
    transformed = []
    for obj in data:
        transformed_obj = transform_mentions(obj)
        transformed.append(transformed_obj)
    return transformed

def main():
    input_file = "DB.json"      # Your input file
    output_file = "DB_new.json"  # Output file for the transformed data

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
