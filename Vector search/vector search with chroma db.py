import chromadb
import json
from tqdm import tqdm

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="new2_collection")

# Step 1: Read the JSON file with explicit encoding
with open('updatedEmbeddedDB (1).json', 'r', encoding='utf-8') as file:
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
        metadatas.append({
            "name": obj["name"],
            "mentions": "\n".join(obj["mentions"]),
            "atlusUrl": obj["atlusUrl"],
            "paper": obj["paper"],
            "paperName": obj["paperName"],
            "image_url": obj.get("image_url", "")
        })
        ids.append(document_id)

    # Step 3: Use the structured data with collection.add
    collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
    results = collection.query(
    query_texts=["this is our document"],
    n_results=3
)