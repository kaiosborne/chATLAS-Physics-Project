# Import relevant libraries
import chromadb
import json
import numpy as np
from tqdm import tqdm
from IPython.display import Image, display
import webbrowser
import csv
from io import StringIO
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI
import os 





# Set the API key
os.environ["OPENAI_API_KEY"] = 'PUT YOUR KEY HERE'

# Set model
llm = OpenAI(model="gpt-3.5-turbo")

# Set query prompt
query_gen_str = """You are a helpful assistant that generates multiple search queries based on a single input query. Generate {num_queries} search queries, one on each line, related to the following input query:
Query: {query}
Queries:
"""
query_gen_prompt = PromptTemplate(query_gen_str)

def generate_queries(query: str, llm, num_queries: int = 4):
    response = llm.predict(
        query_gen_prompt, num_queries=num_queries, query=query
    )
    # assume LLM proper put each query on a newline
    queries = response.split("\n")
    queries_str = "\n".join(queries)
    print(f"Generated queries:\n{queries_str}")
    return queries

queries = generate_queries("What is the efficiency of L1 single EM object triggers vs pile-up?", llm)





# Initialize ChromaDB client and collection
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="new2_collection")

# Step 1: Read the JSON file with explicit encoding
with open('PASA_DB.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Step 2: Process the data
batch_size = 5000  # Set your batch size here
for i in range(0, len(data), batch_size):
    batch_data = data[i:i+batch_size]
    documents = []
    metadatas = []
    ids = []
    embeddings = []

    # Use tqdm for progress visualization
    for j, obj in tqdm(enumerate(batch_data), total=len(batch_data), desc="Adding documents"):
        document_id = f"document_{j}"
        embeddings.append(obj.get("embedded vector", []))
        documents.append(f"{obj['name']} {' '.join(obj['mentions'])}")
        image_urls = obj.get("imageUrls", [])
        metadatas.append({
            "name": obj["name"],
            "mentions": "\n".join(obj["mentions"]),
            "atlusUrl": obj["atlusUrl"],
            "paper": obj["paper"],
            "paperName": obj["paperName"],
            "imageUrls": image_urls
        })
        ids.append(document_id)

    # Use the structured data with collection.add
    results = collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

# Initialise results array
all_results = []

# Apply all queries
for query in queries:
    query_result = collection.query(query_texts=[query], n_results=5)

    # Extract distances and image URLs from each result
    for metadata, distance in zip(query_result['metadatas'][0], query_result['distances'][0]):
        all_results.append((distance, metadata['imageUrls']))

# Sort all_results by distance (the first element of the tuple)
all_results_sorted = sorted(all_results, key=lambda x: x[0])

# Select the top 5 results
top_5_results = all_results_sorted[:5]

# Extract and print the image URLs from these top results
for _, image_url in top_5_results:
    print("Image URL:", image_url)
    webbrowser.open(image_url)

# Print line to separate different generation events for multiple uses - makes it easier to see and debug
print('--------------------------------')

