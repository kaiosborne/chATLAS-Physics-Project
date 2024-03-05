from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
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
response = hybrid_fusion_pack.run("give me feynmann plots")
print(str(response))