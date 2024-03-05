from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from IPython.display import display, Image
import json
import os
os.environ['OPENAI_API_KEY']='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'
# load in some sample data
reader = SimpleDirectoryReader(input_files=["Rawdata (2).json"])
documents = reader.load_data()

## parse nodes
node_parser = SimpleNodeParser.from_defaults()
nodes = node_parser.get_nodes_from_documents(documents)

from llama_index.llama_pack import download_llama_pack

HybridFusionRetrieverPack = download_llama_pack(
    "HybridFusionRetrieverPack",
    "./hybrid_fusion_pack")
hybrid_fusion_pack = HybridFusionRetrieverPack(
    nodes, chunk_size=256, vector_similarity_top_k=2, bm25_similarity_top_k=2)

response = hybrid_fusion_pack.run("give me a lepton decay plot")
print(str(response))
# display the image
#display(image)
import requests
from PIL import Image
from io import BytesIO
import re

# Assume the response is a string and contains a URL
response_str = str(response)

# check if the response contains a URL to an image
if "https://" in response_str and ".png" in response_str:
    url_start = response_str.find("https://")
    url_end = response_str.find(".png", url_start) + 4  # add 4 to include ".png" in the URL
    image_url = response_str[url_start:url_end]

    # Now you can use image_url
    response = requests.get(image_url)
        
    image = Image.open(BytesIO(response.content))

    # Display the image
        
    image.show()

