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

def is_atlus_link(link):
    return link.startswith('https://atlas.web.cern.ch/Atlas') or link.startswith(
            'http://atlas.web.cern.ch/Atlas')

def is_cds_link(link):
    return link.startswith('https://cds.cern.ch/record') or link.startswith('http://cds.cern.ch/record')

def checkIfViableLink(soup,urlNumber,is_link):
    potentialLink = soup.find('a', href=lambda href: href and is_link(href))
    if potentialLink:
        if getNumber(potentialLink['href']) == urlNumber:
            return potentialLink['href']



def getNumber(url):
    return url.rstrip().split("/")[-1]

def find_relevant_link(soup,url):
    """Search for the first relevant hyperlink in the HTML, prioritizing CMS, Atlas, then CDS links."""
    urlNumber = getNumber(url)
    potentialCMSLink = checkIfViableLink(soup,urlNumber,is_cms_link)
    if potentialCMSLink:
        return potentialCMSLink
    
    potentialAtlusLink = checkIfViableLink(soup,urlNumber,is_atlus_link)
    if potentialAtlusLink:
        return potentialAtlusLink
    
    potentialCDSLink = checkIfViableLink(soup,urlNumber,is_cds_link)
    if potentialCDSLink:
        return potentialCDSLink
    return url

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
#            if is_cms and 'thumb' not in img['src']:
#                continue  # Skip this image if it's a CMS link without 'thumb' in the URL

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
            relevant_link = find_relevant_link(soup,url)

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
data_dir = "C:\workspace\git-repos\physics-project\paper data\\New folder"
output_directory = "C:\workspace\git-repos\physics-project\paper data" # Update this path

os.makedirs(output_directory, exist_ok=True)
process_directories(data_dir, output_directory)

#THINGS THAT ARE WRONG

# 1. I have put a kind of filter to prevent the non paper images being scraped but this has added thumb into the URLs
# which means they dont work.
#2. In addition when the images are scraped via the CMS link as opposed to directly on the webpage found in the meta_info.txt file,
#they appear to be saved in a json file that doesnt correspond to the same name as the folder from which they came from.
# So I see stuff like this when it runs : Scraped 46 images from https://cds.cern.ch/record/1460444 into /Users/georgedoumenis-ramos/Documents/DATA SCRAPING/CMS/CMS PAPER IMG URL 3/CDS_Record_1530528.json
