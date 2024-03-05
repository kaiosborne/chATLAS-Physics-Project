import json
import tensorflow as tf
import tensorflow_hub as hub

# Function to load the Universal Sentence Encoder model
def load_model():
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    return model

# Function to generate embedding for the input text
def embed_text(text, model):
    return model([text]).numpy()[0]

# Load the JSON data
with open('Rawdata.json', 'r') as file:
    data = json.load(file)

# Load the embedding model
model = load_model()

# Embed each object and add the "embedded vector" property
# only if it doesn't already exist
for obj in data:  # Assuming 'data' is a list of dictionaries
    if "embedded vector" not in obj:
        # Combining Caption and Mentioned
        text_to_embed = obj.get("Caption", "") + " " + obj.get("mentioned", "")
        # Generate and convert to list
        embedded_vector = embed_text(text_to_embed, model).tolist()
        obj["embedded vector"] = embedded_vector

# Save the modified data back to JSON
with open('EmbeddedDB.json', 'w') as file:
    json.dump(data, file, indent=4)
