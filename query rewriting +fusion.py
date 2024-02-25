from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
import os
os.environ['OPENAI_API_KEY']='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'

from llama_index.llama_pack import download_llama_pack

documents = SimpleDirectoryReader(input_files=["Rawdata (2).json"]).load_data()
node_parser = SimpleNodeParser.from_defaults()
nodes = node_parser.get_nodes_from_documents(documents)

# download and install dependencies
QueryRewritingRetrieverPack = download_llama_pack(
    "QueryRewritingRetrieverPack", "./query_rewriting_pack"
)

# create the pack
query_rewriting_pack = QueryRewritingRetrieverPack(
    nodes,
    chunk_size=256,
    vector_similarity_top_k=2,
)
response = query_rewriting_pack.run("give me a feynmann plot")
print(str(response))
