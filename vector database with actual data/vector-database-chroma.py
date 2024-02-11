import chardet
import json

import chromadb
import json

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="new2_collection")

# Step 1: Read the JSON file with explicit encoding
dir = "C:\workspace\git-repos\physics-project\\vector database with actual data" 
#this directory needs to be changed to your directory (also note \v causes an error you need \\v)
with open(dir+"\\"+'generated-data-small.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Step 2: Process the data
documents = []
metadatas = []
ids = []

for item in data:
    # Check if required keys are present in the item
    if 'name' in item and 'mentions' in item and 'atlusUrl' in item and 'paper' in item and "paperName" in item:
        # Concatenate caption and mentioned for the document
        document = str(item['mentions']+[item["name"]])
        documents.append(document)

        # Create metadata with Plots and web location
        metadata = {"name": item["name"], "atlusUrl": item["atlusUrl"],
                     "paper": item["paper"], "paperName": item["paperName"],
                     "mentions":str(item["mentions"])}
        metadatas.append(metadata)

        # Use Plots value as the ID
        ids.append(f"{item['name']},{item['paper']}")
    else:
        # Handle the case where required keys are missing for an item
        print(f"Skipping item due to missing keys: {item}")

# Step 3: Use the structured data with collection.add
collection.add(documents=documents, metadatas=metadatas, ids=ids)

results = collection.query(
    query_texts=["toroidal field"],
    n_results=3
)
#print(results)

import matplotlib.pyplot as plt
import urllib
from PIL import Image

for i in range(len(results["distances"][0])):
    metadatas = results['metadatas'][0][i]
    print(f"------------Match: {str(i+1)}---------------")
    print(f"Paper Name: {metadatas['paperName']}")
    print(f"Figure name: {metadatas['name']}")
    print(f"Mentions: {metadatas['mentions']}")
    print(f"Web Location: {metadatas['atlusUrl']}")



#this process will not work yet

# # Download and display the picture
# image_url = web_location
# image_path = 'temp_image.png'
# urllib.request.urlretrieve(image_url, image_path)
# img = Image.open(image_path)
# plt.imshow(img)
# plt.axis('off')
# plt.show()
