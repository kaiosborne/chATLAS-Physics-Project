#%%
#Short code to combine databases
import json
def combine_json_files(file_paths, output_file_path):
    combined_data = []

    # Read each JSON file and append its content to combined_data
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            data = json.load(file)
            combined_data.extend(data)

    # Write combined_data to the output JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(combined_data, output_file, indent=4)

# Example usage:
input_files = ["/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS MERGED DATA/MERGED DATA CMS.json", "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/ATLAS CONFERENCE NOTES MERGED DATA/MERGED DATA ATLAS CONFERENCE NOTES.json ", "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS/ATLAS MERGED DATA/MERGED DATA ATLAS.json "]
output_file = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/MERGED DATABASE/MERGED DATA BASE.json"

combine_json_files(input_files, output_file)

#%%
#Short code to remove empty entries i.e. missing imageUrls

def remove_records_with_empty_image_urls(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file:
        combined_data = json.load(input_file)

    # Filter out records with empty "imageUrls"
    combined_data_filtered = [record for record in combined_data if record.get("imageUrls") != []]

    # Write the filtered data to the output JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(combined_data_filtered, output_file, indent=4)

# Example usage:
input_file = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/MERGED DATABASE/MERGED DATA BASE.json"
output_file = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/EMPTY REMOVED/filtered_combined_file.json"

remove_records_with_empty_image_urls(input_file, output_file)
