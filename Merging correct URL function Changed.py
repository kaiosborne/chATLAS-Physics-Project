import json
import os
import re

output_data_json_path = 'C:\workspace\git-repos\physics-project\generated-data.json'
image_url_json_directory = 'C:\workspace\git-repos\physics-project\\'  # Directory containing JSON files for image URLs
updated_output_data_json_path = 'C:\workspace\git-repos\physics-project\OUTPUT\\updated_data.json'


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
    return {}


def update_figures_with_urls(output_data, image_url_json_directory):
    """Update all entries in output data with their corresponding image URLs."""
    for entry in output_data:
        paper_id = entry["paper"]
        image_urls_dict = find_image_urls_for_paper(image_url_json_directory, paper_id)
        entry["imageUrls"] = []

        # Finds figure number from image data
        indexImage = re.search(r"(\d+)", entry["name"]).group(1).lstrip("0")

        for name, url in image_urls_dict.items():
            if re.search(r"aux", name):
                continue

            # Finds figure number in Filename of url
            indexUrl = re.search(r"(\d+)", name).group(1).lstrip("0")
            if indexUrl == indexImage:
                entry["imageUrls"].append(url)


def save_json_data(file_path, data):
    """Save data to a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


# Load the output data JSON
output_data = load_json_data(output_data_json_path)

# Update the output data with image URLs for each entry
update_figures_with_urls(output_data, image_url_json_directory)

# Save the updated output data
save_json_data(updated_output_data_json_path, output_data)