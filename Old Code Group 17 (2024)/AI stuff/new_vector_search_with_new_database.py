import chromadb
import json
from tqdm import tqdm
from IPython.display import Image, display
import webbrowser
import csv
from io import StringIO

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="new2_collection")

# Step 1: Read the JSON file with explicit encoding
with open('MERGED DATA ATLAS.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Step 2: Process the data
batch_size = 5000  # Set your batch size here
for i in range(0, len(data), batch_size):
    batch_data = data[i:i+batch_size]
    documents = []
    metadatas = []
    ids = []
    embeddings = []

    for j, obj in tqdm(enumerate(batch_data), total=len(batch_data), desc="Adding documents"):
        document_id = f"document_{j+i}"
        embeddings.append(obj.get("embedded vector", []))
        documents.append(f"{obj['name']} {' '.join(obj['mentions'])}")
        image_urls = obj.get("imageUrls", [])  # Use the list directly
        image_urls_str = ", ".join(image_urls) if image_urls else ""  # Convert list to string
        metadatas.append({
            "name": obj["name"],
            "mentions": "\n".join(obj["mentions"]),
            "atlusUrl": obj["atlusUrl"],
            "paper": obj["paper"],
            "paperName": obj["paperName"],
            "imageUrls": image_urls_str  # Use the string here
        })
        ids.append(document_id)

    # Step 3: Use the structured data with collection.add
    collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

# Move this block outside the batch processing loop
results = collection.query(query_texts=["What is the the feynman diagram for ZZ production"], n_results=2)
print(results)

# Assuming `result` is the dictionary containing the data
for metadata in results['metadatas'][0]:
    image_urls = csv.reader(StringIO(metadata['imageUrls'])).__next__() if metadata['imageUrls'] else []

    # Open each URL in the default web browser
    for url in image_urls:
        webbrowser.open(url.strip())
