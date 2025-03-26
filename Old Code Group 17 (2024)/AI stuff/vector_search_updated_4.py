# vector_search_embedding.py

import chromadb
import json
from tqdm import tqdm

# Initialize Chroma client and collection
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="collection_for_atlas")

# Function to read JSON and add embeddings to the collection
def add_embeddings_to_collection(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)

    batch_size = 5000
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i+batch_size]
        embeddings = []
        documents = []
        metadatas = []
        ids = []

        for j, obj in tqdm(enumerate(batch_data), total=len(batch_data), desc="Adding documents"):
            document_id = f"document_{j+i}"
            embeddings.append(obj.get("embedded vector", []))
            documents.append(f"{obj['name']} {' '.join(obj['mentions'])}")
            metadatas.append({
                "name": obj["name"],
                "mentions": "\n".join(obj["mentions"]),
                "atlusUrl": obj["atlusUrl"],
                "paper": obj["paper"],
                "paperName": obj["paperName"],
                "imageUrls": obj.get("imageUrls", [])
            })
            ids.append(document_id)
        collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

add_embeddings_to_collection('DB.json')
collections = chroma_client.list_collections()
print(collections)


