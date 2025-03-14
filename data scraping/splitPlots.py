import json
import os

def loadJSON(dataDir, fileName):
    filePath = os.path.join(dataDir, fileName)
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully!")
    except Exception as e:
        print("Error loading JSON:", e)
        data = []
    return data

def saveJSON(data, outputDir, outputName):
    outputPath = os.path.join(outputDir, outputName)
    try:
        with open(outputPath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving JSON:", e)

# Define input and output directories using relative paths
dataDir = os.path.join("Data Scraping", "Test Outputs") 
outputDir = os.path.join("Data Scraping", "Test Outputs")  # temporary test file path (remove Test later)

# Convert to absolute paths if needed
dataDir = os.path.abspath(dataDir)
outputDir = os.path.abspath(outputDir)

#set output file name
fileName = "generated-data5.json"
outputName = "generated-data6.json"

data = loadJSON(dataDir,fileName)
# Process the data: for each original entry, create new entries for each image URL with a letter suffix.
split_entries = []
for entry in data:
    urls = entry.get("imageUrls", [])
    if len(urls) > 1:
        base_name = entry.get("name", "")
        for idx, url in enumerate(urls):
            letter = chr(97 + idx)  # 97 is ASCII for 'a'
            new_entry = entry.copy()  # Create a shallow copy of the original entry
            new_entry["name"] = f"{base_name} ({letter})"  # Append the letter suffix to the name
            new_entry["imageUrls"] = url  # Keep only the current URL
            split_entries.append(new_entry)
    else:
        # If there is only one (or zero) image URL, keep the entry unchanged.
        new_entry = entry.copy()
        new_entry["imageUrls"] = url
        split_entries.append(new_entry)

saveJSON(split_entries,outputDir,outputName)