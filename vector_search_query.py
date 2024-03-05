# vector_search_query.py

import chromadb
import csv
from io import StringIO
import webbrowser

# Initialize Chroma client and access the collection
import chromadb

chroma_client = chromadb.Client()
try:
    # Attempt to get the collection if it already exists
    collection = chroma_client.get_collection(name="collection_for_atlas")
except ValueError as e:
    print(f"Collection not found: {e}")

# Function to query the collection and process results
##def query_collection(query_texts):
    ##results = collection.query(query_texts=query_texts, n_results=5)

    ##for metadata in results['metadatas'][0]:
        ##image_urls = csv.reader(StringIO(metadata['imageUrls'])).__next__() if metadata['imageUrls'] else []
        ##print(image_urls)
        
        ##for url in image_urls:
            ##webbrowser.open(url)
##query_texts = ["What is the the feynman diagram for ZZ production"]
##query_collection(query_texts)

