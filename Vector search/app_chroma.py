from flask import Flask, request, render_template, session, redirect, url_for
import chromadb
import json
from tqdm import tqdm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="PhysicsFigures")

def load_data_into_collection():
    with open('EmbeddedDB_with_images.json', 'r') as file:
        data = json.load(file)

    embeddings = []
    documents = []
    metadatas = []
    ids = []

    for i, obj in tqdm(enumerate(data), total=len(data), desc="Adding documents"):
        document_id = f"document_{i}"
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

    collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)

@app.route('/', methods=['GET'])
def index():
    if 'search_history' not in session:
        session['search_history'] = []
    return render_template('query_form.html', history=session['search_history'])

@app.route('/search', methods=['POST'])
def search():
    query_text = request.form['mainQuery']
    results = collection.query(query_texts=[query_text], n_results=10)

    result_data = [metadata for sublist in results['metadatas'] for metadata in sublist]

    session['search_history'].append({
        'query': query_text,
        'results': result_data[:1]
    })
    session.modified = True

    return render_template('results_page.html', results=result_data)

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
