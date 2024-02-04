from flask import Flask, request, render_template, session
import chromadb
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the ChromaDB client
chroma_client = chromadb.Client()
# Create a collection named "PhysicsFigures"
collection = chroma_client.create_collection(name="PhysicsFigures")

# Function to load and insert data into the collection
def load_data_into_collection():
    with open('Rawdata.json', 'r') as file:
        data = json.load(file)
        documents = []
        metadatas = []
        ids = []

        for obj in data:
            text_content = "{} {}".format(obj['caption'], obj['mentioned'])
            documents.append(text_content)
            metadatas.append({
                "Plot": obj["Plots"],
                "Caption": obj["caption"],
                "Mentioned": obj["mentioned"],
                "WebLocation": obj["web location"]
            })
            ids.append(obj["Plots"])

        collection.add(documents=documents, metadatas=metadatas, ids=ids)

# Load data into the collection when the app starts
load_data_into_collection()

@app.route('/', methods=['GET'])
def index():
    return render_template('query_form.html', history=session.get('search_history'))

@app.route('/search', methods=['POST'])
def search():
    main_query = request.form['mainQuery']
    x_axis = request.form.get('xAxis', '')
    y_axis = request.form.get('yAxis', '')


    # Build the query text by including X and Y axis information if provided
    query_texts = [main_query]
    if x_axis:
        query_texts.append(f"X Axis: {x_axis}")
    if y_axis:
        query_texts.append(f"Y Axis: {y_axis}")

    results = collection.query(query_texts=query_texts, n_results=1)
    
    if not results['metadatas']:
        return render_template('results_page.html', error="No results found")

    top_result_metadata = results['metadatas'][0][0]
    result_data = {
        "Caption": top_result_metadata['Caption'],
        "Mentions": top_result_metadata['Mentioned'],
        "WebLocation": top_result_metadata['WebLocation']
    }
 # Save search query and result to session
    if 'search_history' not in session:
        session['search_history'] = []
    session['search_history'].append({
        'query': main_query,
        'x_axis': x_axis,
        'y_axis': y_axis,
        'results': results['metadatas'][0] if results['metadatas'] else None
    })
    session.modified = True  # To notify Flask that the session has been modified

    return render_template('results_page.html', result=result_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change 5001 to any other port number
