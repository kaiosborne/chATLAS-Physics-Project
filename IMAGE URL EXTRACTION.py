import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm

# Initialize a list to track papers with no images found
papers_with_no_images = []

def scrape_image_data(link):
    """Scrape all PNG image data (name and URL) from the given page, excluding 'cern-logo-large.png'."""
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img', src=lambda src: src.endswith('.png'))  # Filter for PNG images only
        
        # Filter out 'cern-logo-large.png'
        image_data = [{"name": os.path.basename(img['src']), "url": requests.compat.urljoin(link, img['src'])}
                      for img in images if os.path.basename(img['src']) != 'cern-logo-large.png']
        return image_data, True
    except Exception as e:
        print(f"An error occurred while scraping PNG images: {e}")
        return [], False

def find_and_scrape_links(url):
    """Append '/plots' to the original URL and find the CERN link to scrape images."""
    image_data_list = []
    cern_link_found = False

    # Directly append '/plots' to the original URL and scrape images
    plots_url = url + '/plots'
    image_data, plots_scraped = scrape_image_data(plots_url)
    image_data_list += image_data

    # Attempt to find and scrape the CERN link
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    atlas_link = soup.find('a', href=lambda href: href and href.startswith('https://atlas.web.cern.ch/Atlas'))
    if atlas_link:
        cern_url = atlas_link['href']
        # Check for and remove a trailing full stop
        if cern_url.endswith('.'):
            cern_url = cern_url[:-1]
        image_data, cern_scraped = scrape_image_data(cern_url)
        image_data_list += image_data
        cern_link_found = cern_scraped
    
    return image_data_list, cern_link_found

def process_meta_info(meta_info_path, output_directory):
    """Process each meta_info.txt file to scrape PNG images from the original URL with '/plots' and check for the CERN link."""
    folder_name = os.path.basename(os.path.dirname(meta_info_path))
    with open(meta_info_path) as file:
        content = file.read()

    prefix = "URL : "
    start = content.find(prefix)
    if start != -1:
        start += len(prefix)
        original_url = content[start:].strip().split("\n", 1)[0]

        image_data_list, cern_link_found = find_and_scrape_links(original_url)

        if image_data_list:
            output_data = {
                "images": image_data_list,
                "cern_link_found": cern_link_found
            }
            output_path = os.path.join(output_directory, f"{folder_name}.json")
            with open(output_path, 'w') as json_file:
                json.dump(output_data, json_file, indent=4)
            print(f"Scraped {len(image_data_list)} PNG images into {output_path}. CERN link found: {cern_link_found}")
        else:
            print(f"No PNG images found for {folder_name}. CERN link found: {cern_link_found}")
            papers_with_no_images.append(folder_name)
    else:
        print(f"URL prefix '{prefix}' not found in {meta_info_path}")
        papers_with_no_images.append(folder_name)

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
data_dir = "/Users/georgedoumenis-ramos/Documents/ATLAS PUBLICATIONS TEST"  # Update this path
output_directory = "/Users/georgedoumenis-ramos/Documents/IMAGE URL TEST"  # Update this path

os.makedirs(output_directory, exist_ok=True)

process_directories(data_dir, output_directory)
