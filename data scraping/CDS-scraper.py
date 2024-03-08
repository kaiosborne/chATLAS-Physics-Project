"""
author = Runze Li
email = runze.li@yale.edu
"""
import os
import subprocess
import numpy as np
import re
import subprocess
import shutil
import sys

from bs4 import BeautifulSoup
import PyPDF2
import requests
import time


# retrieve the name liek CDS_Record_12345 from url
def url_to_folder_name(url):
    # Regular expression to extract the record number
    match = re.search(r'record/(\d+)', url)
    if match:
        record_number = match.group(1)
        folder_name = f"CDS_Record_{record_number}"
        return folder_name
    else:
        return "Invalid_URL"

# find the minimal value in input sequence, used to check the min between
# page num of Author list and page num of Acknowledgement to determine where we stop
def min_of_list(values):
    # Filter out None values
    filtered_values = [v for v in values if v is not None]
    
    if not filtered_values:  # Check if the list is empty
        return -1
    else:
        return min(filtered_values)


# get the pdf link from the paper's cds url and download it
def download_pdf(url):
    # Get the content from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the PDF link in the meta tags
    meta_tag = soup.find('meta', attrs={'name': 'citation_pdf_url'})
    pdf_name = ""

    if meta_tag:
        pdf_url = meta_tag['content']
        pdf_name = pdf_url.split("/")[-1][:-4]

        # Download the PDF
        response_pdf = requests.get(pdf_url)
        if response_pdf.status_code == 200:   # get the pdf file
            with open(f"./{pdf_name}.pdf", 'wb') as f:
                f.write(response_pdf.content)
        else:
            print(f'Failed to download PDF from {pdf_url}')  # then we do not care about images
            return 1  # PDF download failed

    else:
        print('No citation_pdf_url meta tag found.') # then we do not care about images
        return 1  # No meta tag found

    # Return the results
    return pdf_name
    
# get the last modification date metadata from cds paper page
def get_modification_date(url):
    # Get the content from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element containing the last modification date
    modification_div = soup.find("div", class_="recordlastmodifiedbox")
    
    # Extract the text and clean it up
    if modification_div:
        modification_text = modification_div.get_text(strip=True)
        # Extracting the last modified date from the text
        last_modified_date = modification_text.split("last modified")[-1].strip()
        return last_modified_date
    else:
        return None

# use nougat to extract text
def extract_text(file_dir, output_directory, page_to_stop):
    try:
        # Build the command
        if page_to_stop == -1:   # if we cannot find an early stopping page defined by Author list or etc
            cmd = ["nougat", file_dir + ".pdf", "-o", output_directory]
        else:  # if we do find that, we only scrape page 1 to that page
            cmd = ["nougat", file_dir + ".pdf", "-o", output_directory, "-p", "1-" + str(page_to_stop)]

        print(cmd)

        # Start the subprocess
        process = subprocess.Popen(cmd)

        # Wait for the process to complete (with or without a timeout)
        process.wait()

        # Check the exit code of the process
        if process.returncode != 0:
            print(f"Process ended with an error code: {process.returncode}")
            # Handle error case as needed
        else:
            # Rename the file as needed if the process completed successfully
            os.rename(output_directory + file_dir + ".mmd", output_directory +"latex.txt")

    except subprocess.CalledProcessError as e:
        print("An error occurred while reading the pdf.")
        print(e)
    except Exception as e:
        print("An unexpected error occurred.")
        print(e)


# look for key word in the pdf, such as Author list or etc
def find_key_in_pdf(file_path, keyword):
    try:
        # Open the PDF file
        with open(file_path + ".pdf", 'rb') as file:
            reader = PyPDF2.PdfReader(file)
    
            # Iterate through each page, starting from the last page
            for page_num in range(len(reader.pages) - 1, -1, -1):
                page = reader.pages[page_num]
                text = page.extract_text()
    
                if text and keyword in text:
                    return page_num + 1  # Return page number (1-indexed)
    
        return None
    except:
        return None


# get links to all papers and their titles in main url (paper list)
def get_paper_links(url):
    paper_links = []
    paper_titles = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    for titlelink in soup.find_all('a', class_='titlelink'):

        # Print or process the title and the description
        title = titlelink.text

        url = titlelink['href']

        # Normalize the URL by removing the query string for language
        if url.endswith("?ln=en"):
            url = url[:-6]

        if "[...]" not in title:
            paper_links.append(url)
            paper_titles.append(title)
    
    return paper_links, paper_titles


"""
Starting from base url, find all links on this page, and go to the next page
each page in main url like https://cds.cern.ch/search?cc=CERN+Preprints&jrec=1 contains 10 papers, so we go as
jrec = 1, 11, 21, ... until what is defined by depth
depth * 10 is the total amount of papers we loop through

then read pdf url from paper's url, and write the paper to database
"""
def write_to_db(base_url, depth, db_dir):

    # instead of stop at fixed depth, may want to change into while loop and stop when no file found (reach the end)
    
    for i in range(depth):
        print("curr depth "  + str(i) + " in " + str(depth))

        fail_file = open("./failed_list.txt", 'a')

        # so depth is n, then i is 1, 11, ..., 10*(n-1) + 1
        page_index = i * 10 + 1

        # get the url of this page
        url = base_url.format(page_index=page_index)

        # loop through all links on this page, should find 10 paper links, only keep those with "ATLAS" keyword
        links, titles = get_paper_links(url)

        for link, title in zip(links, titles):

            folder_name = url_to_folder_name(link)

            # may need to change if we want to update rather than just collect
            if os.path.exists(db_dir + "/" + folder_name + "/latex.txt") and os.path.exists(db_dir + "/" + folder_name + "/meta_info.txt"):
                continue # already exist
                
            print("\n\n\nwork on link " + link)
            # have to download it before nougat can read it in locally
            pdf_name = download_pdf(link)

            last_modification_date = get_modification_date(link)
    
            if pdf_name != 1:
                
                if not os.path.exists(db_dir + "/" + folder_name + "/"):
                    os.mkdir(db_dir + "/" + folder_name + "/")
    
                else:
                    try:
                        shutil.rmtree(db_dir + "/" + folder_name + "/temp/")
                    except:
                        pass
    
                
                last_page_num_References = find_key_in_pdf(pdf_name, "References")
                #last_page_num_The_ATLAS_Collaboration = find_key_in_pdf(pdf_name, "The ATLAS Collaboration")  
                #remove this because sometimes it shows up in the very beginning :(
                last_page_num_acknowledgement = find_key_in_pdf(pdf_name, "ACKNOWLEDGMENT")
    
                page_to_stop = min_of_list([last_page_num_References, last_page_num_acknowledgement])
    
                print("last reference at " + str(last_page_num_References) + " last acknowledge at " + str(last_page_num_acknowledgement))
                print("end at " + str(page_to_stop))
    
                try:
                    extract_text(pdf_name, db_dir + "/" + folder_name + "/", page_to_stop)
                    meta_info = open(db_dir + "/" + folder_name + "/meta_info.txt", 'w')
                    meta_info.write("PAPER NAME : ")
                    meta_info.write(title.replace("\n", "")+"\n")
                    meta_info.write("LAST MODIFICATION DATE : ")
                    meta_info.write(last_modification_date + "\n")
                    meta_info.write("URL : ")
                    meta_info.write(link.replace("\n", "") + "\n")
                    meta_info.close()
                except:
                    fail_file_after_nougat.write(link + "\n")
    
                    print("\n fail to read " + link + "\n")
    
            
                if os.path.exists(pdf_name + ".pdf"):
                    os.remove(pdf_name + ".pdf")
    
            else:
                fail_file_after_nougat.write(link + "\n")
    
                print("\n fail to read " + link + "\n")
    
        fail_file.close()


# Change this to your path
db_dir = "./"

if not os.path.exists(db_dir + "CDS_doc"):
    os.mkdir(db_dir + "CDS_doc")

# around 1200 pdfs
base_url_ATLAS_paper = "https://cds.cern.ch/search?cc=ATLAS+Papers&jrec={page_index}"

# around 2560 pdfs
base_url_ATLAS_preprint = "https://cds.cern.ch/search?cc=ATLAS+Preprints&m1=a&jrec={page_index}"

base_url_ATLAS_pub_notes = "https://cds.cern.ch/search?cc=ATLAS+PUB+Notes&m1=a&jrec={page_index}"

base_url_ATLAS_internal_notes = "https://cds.cern.ch/search?cc=ATLAS+Internal+Notes&m1=a&jrec={page_index}"

write_to_db(base_url_ATLAS_pub_notes, 10, db_dir + "CDS_doc")








