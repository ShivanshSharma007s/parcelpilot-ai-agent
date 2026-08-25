import os
import sys
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INDEX_PATH, DOC_CHUNKS_PATH

def search_documents(query, top_n=3):
    if not os.path.exists(INDEX_PATH) or not os.path.exists(DOC_CHUNKS_PATH):
        return {"error": "Document index not found. Please run data ingestion first."}
        
    with open(INDEX_PATH, 'rb') as f:
        bm25 = pickle.load(f)
        
    with open(DOC_CHUNKS_PATH, 'rb') as f:
        all_chunks = pickle.load(f)
        
    tokenized_query = query.lower().split()
    # Get top n
    top_docs = bm25.get_top_n(tokenized_query, all_chunks, n=top_n)
    
    results = []
    for doc in top_docs:
        results.append({
            "content": doc["text"],
            "metadata": doc["metadata"]
        })
        
    if not results:
        return {"message": "No relevant documents found."}
        
    return {"results": results}
