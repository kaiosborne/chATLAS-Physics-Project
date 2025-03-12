from flask import Flask, request, render_template, session, redirect, url_for
import chromadb
import json
import os
from tqdm import tqdm
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="PhysicsFigures")

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, './DB.json') #sets database path to current directory with name DB.json

def load_data_into_collection():
    with open(db_path, 'r') as file:
        data = json.load(file)

    batch_size = 40000  
    total_documents = len(data)
    num_batches = (total_documents + batch_size - 1) // batch_size  # Calculate the total number of batches

    for batch_num in tqdm(range(num_batches), desc="Processing batches"):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, total_documents)
        batch_data = data[start_idx:end_idx]

        embeddings = []
        documents = []
        metadatas = []
        ids = []

        for i, obj in enumerate(batch_data):
            document_id = f"document_{start_idx + i}"
            embeddings.append(obj.get("embedded vector", []))
            documents.append(f"{obj['name']} {' '.join(obj['mentions'])}")
            metadatas.append({
                "name": obj["name"],
                "mentions": "\n".join(obj["mentions"]),
                "atlusUrl": obj["atlusUrl"],
                "paper": obj["paper"],
                "paperName": obj["paperName"],
                "image_url": obj.get("imageUrls", "")
            })
            ids.append(document_id)

        collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

        tqdm.write(f"Added documents {start_idx} to {end_idx-1} to the collection")

@app.route('/', methods=['GET'])
def index():
    if 'search_history' not in session:
        session['search_history'] = []
    return render_template('query_form2.html', history=session['search_history'])

@app.route('/search', methods=['POST'])
def search():
    query_text = request.form['mainQuery']
    
    # Run embedding-based search
    embedding_results = collection.query(query_texts=[query_text], n_results=10)

    print(f"embedding results {embedding_results}")

    # Extract embedding-based results
    embedding_data = [
        metadata for sublist in embedding_results['metadatas'] for metadata in sublist
    ]

    # Run keyword-based search on metadata fields (adds to results)
    #keyword_matches = []
    #for obj in collection.get()['metadatas']:
        #text_to_search = f"{obj.get('keywords', '')}".lower()
        #if re.search(r'\b' + re.escape(query_text.lower()) + r'\b', text_to_search):
            #keyword_matches.append(obj)

    # Combine results - using a set to remove duplicates + keyword matches
    combined_results = {obj['paperName']: [] for obj in embedding_data}
    
    # Grouping results by paperName
    for result in embedding_data:
        combined_results[f'{result['paperName']}'].append(result)
    # Convert to a list of tuples to send to the template
    grouped_results = [(paper_name, figures) for paper_name, figures in combined_results.items()]
    # Store search history
    session['search_history'].append({
        'query': query_text,
        'results': grouped_results[:5]  # Limit displayed results
    })
    session.modified = True

    return render_template('results_page2.html', results=grouped_results)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session.pop('search_history', None)
    return redirect(url_for('index'))

@app.route('/play-invisible-atom')
def play_invisible_atom():
    return render_template('invisible_atom.html')

if __name__ == '__main__':
    load_data_into_collection()
    app.run(debug=True, port=5001)





