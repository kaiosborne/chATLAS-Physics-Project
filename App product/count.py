import json
from tqdm import tqdm
import os

# Load JSON data from file

dataDir = os.path.join("App product")
fileName = 'DB.json'


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


data = loadJSON(dataDir,fileName)

# Count figures (assuming each JSON object corresponds to one figure)
# If the JSON is a list of such objects, count the elements in the list.
if isinstance(data, list):
    num_figures = 0
    for _ in tqdm(data, desc="Processing Figures"):
        num_figures += 1
else:
    num_figures = 1  # Single figure object

print(f"Number of figures: {num_figures}")