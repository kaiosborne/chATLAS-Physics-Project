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


import unittest
from chatlas import ChatlasEngine  # Replace with the actual module

class TestChatlasReliability(unittest.TestCase):

    def setUp(self):
        self.chatlas = ChatlasEngine()

    def test_invalid_input(self):
        # Test how Chatlas handles invalid inputs
        response = self.chatlas.get_response("")
        self.assertEqual(response, "Please provide a valid input.")

    def test_database_failure(self):
        # Simulate a database failure
        with patch('chatlas.DatabaseAPI.get_user_data', side_effect=Exception("Database error")):
            response = self.chatlas.get_response("What is my name?")
            self.assertEqual(response, "Sorry, I'm unable to process your request at the moment.")

    def tearDown(self):
        self.chatlas = None

if __name__ == "__main__":
    unittest.main()


import pytest
from chatlas import ChatlasEngine
from unittest.mock import Mock

def test_database_integration():
    # Mock the database
    mock_db = Mock()
    mock_db.get_user_data.return_value = {"name": "John Doe"}

    # Initialize Chatlas with the mock database
    chatlas = ChatlasEngine(database=mock_db)

    # Test fetching user data
    response = chatlas.get_response("What is my name?")
    assert response == "Your name is John Doe."

def test_api_integration():
    # Mock an external API
    mock_api = Mock()
    mock_api.get_weather.return_value = {"weather": "sunny"}

    # Initialize Chatlas with the mock API
    chatlas = ChatlasEngine(weather_api=mock_api)

    # Test weather API integration
    response = chatlas.get_response("What's the weather?")
    assert "sunny" in response

def test_authentication():
    # Mock an authentication service
    mock_auth = Mock()
    mock_auth.authenticate.return_value = True

    # Initialize Chatlas with the mock authentication service
    chatlas = ChatlasEngine(auth_service=mock_auth)

    # Test authentication
    response = chatlas.get_response("Login as admin")
    assert "Welcome, admin" in response


import pytest
import requests

CHATLAS_API_URL = "https://api.chatlas.com/v1/chat"

def test_sql_injection():
    # Test for SQL injection vulnerability
    response = requests.post(CHATLAS_API_URL, json={"message": "' OR 1=1 --"})
    assert "error" not in response.json(), "SQL injection vulnerability detected!"

def test_xss():
    # Test for XSS vulnerability
    response = requests.post(CHATLAS_API_URL, json={"message": "<script>alert('XSS')</script>"})
    assert "<script>" not in response.json()["reply"], "XSS vulnerability detected!"

def test_unauthorized_access():
    # Test if unauthorized users are blocked
    response = requests.post(CHATLAS_API_URL, json={"message": "Admin command"}, headers={"Authorization": "InvalidToken"})
    assert response.status_code == 401, "Unauthorized access allowed!"

def test_data_encryption():
    # Test if sensitive data is encrypted
    response = requests.post(CHATLAS_API_URL, json={"message": "My credit card is 1234-5678-9012-3456"})
    assert "1234-5678-9012-3456" not in response.json()["reply"], "Sensitive data is not encrypted!"

