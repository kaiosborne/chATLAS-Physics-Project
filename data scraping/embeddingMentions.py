import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm  # Import tqdm

# Function to load the Sentence Transformer model
def load_model():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model

# Function to generate embedding for the input text
def embed_text(text, model):
    return model.encode([text])[0]

# Load the JSON data
with open('generated-data 2.json', 'r') as file:  # Make sure this matches your JSON file's name
    data = json.load(file)

# Load the embedding model
model = load_model()

for obj in tqdm(data, desc="Generating embeddings"):  # Wrap 'data' with tqdm for the progress bar
    if "embedded vector" not in obj:
        text_to_embed = f"{obj.get('name', '')} {' '.join(obj.get('mentions', []))} {obj.get('atlusUrl', '')} {obj.get('paper', '')} {obj.get('paperName', '')}"
        embedded_vector = embed_text(text_to_embed, model).tolist()
        obj["embedded vector"] = embedded_vector

# Save the modified data back to a new JSON file
with open('EmbeddedDB.json', 'w') as file:
    json.dump(data, file, indent=4)
