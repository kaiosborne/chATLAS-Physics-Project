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
with open('DB.json', 'r', encoding='utf-8') as file:
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
        image_urls = obj.get("imageUrls", [])  # Get the list directly
        metadatas.append({
            "name": obj["name"],
            "mentions": "\n".join(obj["mentions"]),
            "atlusUrl": obj["atlusUrl"],
            "paper": obj["paper"],
            "paperName": obj["paperName"],
            "imageUrls": image_urls  # Use the list directly
        })
        ids.append(document_id)

    # Use the structured data with collection.add
    collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
results = collection.query(
query_texts=["Data vs simulation comparison of the S_T variable in the leptoquark search for with bτ decays"],
n_results=5
)
##print(results)


##import webbrowser

# Assuming `result` is the dictionary containing the data
for metadata in results['metadatas'][0]:
    image_urls = csv.reader(StringIO(metadata['imageUrls'])).__next__() if metadata['imageUrls'] else []
    print(image_urls)
    
    # Open each URL in the default web browser
    for url in image_urls:
        webbrowser.open(url)





