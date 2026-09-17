import os
from src import config

def prepare_rag_payload(vector_db, query_text: str):
    """Retrieves 6 chunks, extracts sources, and builds the raw prompt string."""
    # 1. Retrieve the top 6 most relevant context fragments
    retrieved_docs = vector_db.similarity_search(query_text, k=6)
    
    # 2. Extract and format unique source references from metadata
    sources = set()
    for doc in retrieved_docs:
        filename = os.path.basename(doc.metadata.get("source", "Unknown File"))
        page = doc.metadata.get("page", None)
        if page is not None:
            sources.add(f"📖 {filename} (Page {page + 1})")
        else:
            sources.add(f"📖 {filename}")

    # 3. Combine text chunks into a context pool
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 4. Construct the clean, multi-line prompt structure
    prompt = f"""
You are a precise academic assistant. 
Answer the question comprehensively using ONLY the context provided below. 
Provide deep context and elaborate on technical details found in the text.

If you do not know the answer or if it's not explicitly mentioned in the context, say "I cannot find that in the documents."

CONTEXT:
{context}

QUESTION:
{query_text}

ANSWER:
"""
    return prompt, sorted(list(sources))
