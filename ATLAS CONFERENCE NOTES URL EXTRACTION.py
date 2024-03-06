#%%
import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm  # Import tqdm for the progress bar

# Initialize lists to track papers
papers_with_no_images = []


def find_relevant_link(soup):
    """Search for the first relevant hyperlink in the HTML, prioritizing Atlas links, then CDS links."""
    atlas_link = soup.find('a', href=lambda href: href and (
                href.startswith('https://atlas.web.cern.ch/Atlas') or href.startswith(
            'http://atlas.web.cern.ch/Atlas')))
    if atlas_link:
        return atlas_link['href']

    cds_link = soup.find('a', href=lambda href: href and (
                href.startswith('https://cds.cern.ch/record') or href.startswith('http://cds.cern.ch/record')))
    return cds_link['href'] if cds_link else None


def scrape_image_data(link):
    """Scrape all image data (name and URL) from the given page, filtering out names not starting with '.thumb'."""
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img', src=True)

        image_data = [{"name": os.path.basename(img['src']), "url": link+"//"+ img['src']} for img
                      in images if os.path.basename(img['src']).startswith(".thumb")]
        return image_data
    except Exception as e:
        print(f"An error occurred while scraping images: {e}")
        return []


def process_meta_info(meta_info_path, output_directory):
    """Process each meta_info.txt file to scrape images from linked pages, handling both Atlas and CDS links, and filtering based on name."""
    folder_name = os.path.basename(os.path.dirname(meta_info_path))  # Define folder_name at the start
    with open(meta_info_path) as file:
        content = file.read()

    prefix = "URL : "
    start = content.find(prefix)
    if start != -1:
        start += len(prefix)
        url = content[start:].strip().split("\n", 1)[0]

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            relevant_link = find_relevant_link(soup)

            if relevant_link:
                image_data = scrape_image_data(relevant_link)
                print(image_data)
                if image_data:
                    output_path = os.path.join(output_directory, f"{folder_name}.json")
                    with open(output_path, 'w') as json_file:
                        json.dump(image_data, json_file, indent=4)
                    print(f"Scraped {len(image_data)} images from {relevant_link} into {output_path}")
                else:
                    print(f"No images found at {relevant_link}")
                    papers_with_no_images.append(folder_name)
            else:
                print(f"No relevant link found in {url}")
                papers_with_no_images.append(folder_name)
        except requests.RequestException as e:
            print(f"Failed to process URL {url}: {e}")
            papers_with_no_images.append(folder_name)
    else:
        print(f"URL prefix '{prefix}' not found in {meta_info_path}")
        papers_with_no_images.append(folder_name)
        output_path = os.path.join(output_directory, f"{folder_name}.json")
        with open(output_path, 'w') as json_file:
            json.dump(image_data, json_file, indent=4)


def process_directories(data_dir, output_directory):
    """Traverse directories to find and process meta_info.txt files, and report papers with no images found."""
    meta_info_paths = []  # Collect all meta_info.txt paths first
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith("meta_info.txt"):
                meta_info_path = os.path.join(root, filename)
                meta_info_paths.append(meta_info_path)

    # Now process each meta_info.txt with a progress bar
    for meta_info_path in tqdm(meta_info_paths, desc="Processing meta_info.txt files"):
        process_meta_info(meta_info_path, output_directory)

    # After processing, report papers with no images found
    if papers_with_no_images:
        print("\nPapers with no images found:")
        for paper in papers_with_no_images:
            print(paper)


# Configuration
data_dir = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/ATLAS CONFERENCE NOTES Papers"  # Update this path
output_directory = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/ATLAS CONFERENCE NOTES/ATLAS CONFERENCE NOTES PAPER IMG URL"  # Update this path

os.makedirs(output_directory, exist_ok=True)

process_directories(data_dir, output_directory)