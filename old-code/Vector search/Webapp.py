import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
import tensorflow as tf
import tensorflow_hub as hub
from IPython.display import Image, display

# Function to load the Universal Sentence Encoder model
def load_model():
    return hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# Function to generate embedding for the input text
def embed_text(text, model):
    return model([text]).numpy()[0]

# Function to load data from JSON and prepare for KNN
def load_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    vectors = []
    info = []
    for obj in data:  # Assuming data is a list of dictionaries
        if "embedded vector" in obj:
            vectors.append(obj["embedded vector"])
            info.append((obj["Plots"], obj["caption"], obj["mentioned"], obj["web location"]))
    return np.array(vectors), info

# Function to perform KNN search
def knn_search(query, model, vectors, info, n_neighbors=1):
    query_vector = embed_text(query, model)
    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(vectors)
    distances, indices = nbrs.kneighbors([query_vector])
    closest = indices[0][0]
    return info[closest]

# Main function to use for search
def vector_search(query):
    model = load_model()
    vectors, info = load_data('EmbeddedDB.json')
    closest_match = knn_search(query, model, vectors, info)
    return closest_match

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        result = vector_search(query)
        plots, caption, mentioned, web_location = result
        # Since the image is at a web location, it can be used directly in the template
        return render_template('result.html', plots=plots, caption=caption, mentioned=mentioned, web_location=web_location)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
