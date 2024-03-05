import json
import os
import re

# Define paths
output_data_json_path = '/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS PAPER DATA/CMS GENERATED DATA.json'
image_url_json_directory = '/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS PAPER IMG URL 2'
updated_output_data_json_path = '/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS MERGED DATA/MERGED DATA CMS.json'

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_image_urls_for_paper(image_url_json_directory, paper_id):
    json_path = os.path.join(image_url_json_directory, f"{paper_id}.json")
    if os.path.isfile(json_path):
        return load_json_data(json_path)
    else:
        print(f"File not found for paper ID: {paper_id}")
    return []

def update_figures_with_urls(output_data, image_url_json_directory):
    for entry in output_data:
        paper_id = entry.get("paper")
        image_urls = find_image_urls_for_paper(image_url_json_directory, paper_id)
        entry["imageUrls"] = []

        for img in image_urls:
            if 'Figure' in entry['name'] and 'Figure' in img['name'] or 'Table' in entry['name'] and 'Table' in img['name']:
                entry_num = entry['name'].split()[-1]
                img_num = re.findall(r'\d+', img['name'])[0]
                if entry_num.zfill(3) == img_num.zfill(3):
                    entry["imageUrls"].append(img["url"])

def save_json_data(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

output_data = load_json_data(output_data_json_path)
update_figures_with_urls(output_data, image_url_json_directory)
save_json_data(updated_output_data_json_path, output_data)

