import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm  # Import tqdm
import os

dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")
fileName = "generated-data5.json"

def loadJSON(dataDir, fileName):
    filePath = os.path.join(dataDir, fileName)
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully!")
    except Exception as e:
        print("Error loading JSON:", e)
        data = []
    return data

def saveJSON(data, outputDir, outputName):
    outputPath = os.path.join(outputDir, outputName)
    try:
        with open(outputPath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving JSON:", e)

# Function to load the Sentence Transformer model
def load_model():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model

# Function to generate embedding for the input text
def embed_text(text, model):
    return model.encode([text])[0]

# Load the JSON data
data = loadJSON(dataDir,fileName)

# Load the embedding model
model = load_model()

for obj in tqdm(data, desc="Generating embeddings"):  # Wrap 'data' with tqdm for the progress bar
    if "embeddedVector" not in obj:
        text_to_embed = f"{' '.join(obj.get('mentions', []))}{obj.get('paperName', '')}{obj.get('keywords', '')}{obj.get('mathsDefinitions', '')}"
        embedded_vector = embed_text(text_to_embed, model).tolist()
        obj["embeddedVector"] = embedded_vector

saveJSON(data,outputDir,outputName='EmbeddedDB.json')
# Save the modified data back to a new JSON file
print("Embeddings saved to JSON!")

#with open('EmbeddedDB.json', 'w') as file:
    #json.dump(data, file, indent=4)
