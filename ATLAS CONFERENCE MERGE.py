#%%

import json
import os
import re




dataNotFoundLoc =  "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/ATLAS CONFERENCE NOTES DATA NOT FOUND\\data-not-found.txt"
output_data_json_path = '/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/ATLAS CONFERENCE NOTES PAPER DATA/generated-data.json'
image_url_json_directory = '/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/ATLAS CONFERENCE NOTES PAPER IMG URL'  # Directory containing JSON files for image URLs
updated_output_data_json_path = '/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/MERGED DATA ATLAS CONFERENCE NOTES.json '

dataNotFoundLoc

dataNotFoundList = []

def load_json_data(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def find_image_urls_for_paper(image_url_json_directory, paper_id):
    """Find the JSON file for a given paper ID and extract image URLs."""
    json_path = os.path.join(image_url_json_directory, f"{paper_id}.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            image_data = json.load(file)
        return {img['name']: img['url'] for img in image_data}
    else:
        dataNotFoundList.append(paper_id)
    return {}


def update_figures_with_urls(output_data, image_url_json_directory):
    """Update all entries in output data with their corresponding image URLs."""
    for entry in output_data:
        paper_id = entry["paper"]
        image_urls_dict = find_image_urls_for_paper(image_url_json_directory, paper_id)

        entry["imageUrls"] = []

        # Finds figure number from image data
        indexImageMatch = re.search(r"(\d+)", entry["name"])
        if indexImageMatch:
            indexImage = indexImageMatch.group(1).lstrip("0")
        else:
            continue  # Skip this entry if no figure number is found in the entry name

        for name, url in image_urls_dict.items():
            if re.search(r"aux", name):
                continue

            # Finds figure number in Filename of url
            indexUrlMatch = re.search(r"(\d+)", name)
            if indexUrlMatch:
                indexUrl = indexUrlMatch.group(1).lstrip("0")
                if indexUrl == indexImage:
                    if re.search("[fF]ig", name) and re.search("[fF]ig", entry["name"]):
                        entry["imageUrls"].append(url)
                    elif re.search("[tT]ab", name) and re.search("[tT]ab", entry["name"]):
                        entry["imageUrls"].append(url)
            else:
                continue  # Skip this URL if no figure number is found in the URL name



def save_json_data(file_path, data):
    """Save data to a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


# Load the output data JSON
output_data = load_json_data(output_data_json_path)

# Update the output data with image URLs for each entry
update_figures_with_urls(output_data, image_url_json_directory)

# Filter out cases with no images
output_data = [i for i in output_data if i["imageUrls"] !=[]]

# Save the updated output data
save_json_data(updated_output_data_json_path, output_data)

# Removes repeats of files where data can't be found
dataNotFoundList = list(set(dataNotFoundList))

# Saves data not found file
save_json_data(dataNotFoundLoc, dataNotFoundList)