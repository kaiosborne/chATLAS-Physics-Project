import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm  # Import tqdm for the progress bar
from urllib.parse import urljoin  # For proper URL concatenation

# Initialize lists to track papers
papers_with_no_images = []

def is_cms_link(link):
    """Check if the link is a CMS link."""
    return link.startswith('http://cms-results.web.cern.ch/cms-results/public-results/publications') or \
           link.startswith('https://cms-results.web.cern.ch/cms-results/public-results/publications')

def find_relevant_link(soup):
    """Search for the first relevant hyperlink in the HTML, prioritizing CMS, Atlas, then CDS links."""
    cms_link = soup.find('a', href=lambda href: href and is_cms_link(href))
    if cms_link:
        return cms_link['href']

    atlas_link = soup.find('a', href=lambda href: href and (
                href.startswith('https://atlas.web.cern.ch/Atlas') or href.startswith(
            'http://atlas.web.cern.ch/Atlas')))
    if atlas_link:
        return atlas_link['href']

    cds_link = soup.find('a', href=lambda href: href and (
                href.startswith('https://cds.cern.ch/record') or href.startswith('http://cds.cern.ch/record')))
    return cds_link['href'] if cds_link else None

def scrape_image_data(link):
    """Scrape all image data (name and URL) from the given page, filtering CMS links by 'thumb'."""
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img', src=True)

        # Determine if the link is a CMS link
        is_cms = is_cms_link(link)

        image_data = []
        for img in images:
            img_url = urljoin(link, img['src'])

            # Apply the 'thumb' filter conditionally for CMS links
            if is_cms and 'thumb' not in img['src']:
                continue  # Skip this image if it's a CMS link without 'thumb' in the URL

            # For CMS links with 'thumb' and all non-CMS links, add the image data
            image_data.append({"name": os.path.basename(img['src']), "url": img_url})

        return image_data
    except Exception as e:
        print(f"An error occurred while scraping images: {e}")
        return []

def process_meta_info(meta_info_path, output_directory):
    """Process each meta_info.txt file to scrape images from linked pages."""
    folder_name = os.path.basename(os.path.dirname(meta_info_path))
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

def process_directories(data_dir, output_directory):
    """Traverse directories to find and process meta_info.txt files."""
    meta_info_paths = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith("meta_info.txt"):
                meta_info_path = os.path.join(root, file)
                meta_info_paths.append(meta_info_path)

    for meta_info_path in tqdm(meta_info_paths, desc="Processing meta_info.txt files"):
        process_meta_info(meta_info_path, output_directory)

    if papers_with_no_images:
        print("\nPapers with no images found:")
        for paper in papers_with_no_images:
            print(paper)

# Example configuration - update these paths as needed
data_dir = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS Papers"  # Update this path
output_directory = "/Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS PAPER IMG URL 2"  # Update this path

os.makedirs(output_directory, exist_ok=True)
process_directories(data_dir, output_directory)

