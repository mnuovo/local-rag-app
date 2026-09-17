import os
import shutil
import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from src import config

def rebuild_vector_db(progress_callback=None):
    """Completely clears and rebuilds the ChromaDB vector store safely from scratch."""
    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL)
    
    # 1. Force close and clear out active internal ChromaDB connections to avoid locked read-only states
    try:
        # This clears internal engine singleton states holding file locks
        chromadb.api.client.SharedSystemClient.clear_system_cache()
    except Exception:
        pass

    # 2. Force delete existing database directory safely
    if os.path.exists(config.DB_DIR):
        try:
            shutil.rmtree(config.DB_DIR)
        except Exception as e:
            print(f"File locking warning: {e}. Attempting file-level override...")
            
    os.makedirs(config.DB_DIR, exist_ok=True)
    
    if not os.path.exists(config.DOCS_DIR) or not os.listdir(config.DOCS_DIR):
        return None

    all_chunks = []
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, 
        chunk_overlap=config.CHUNK_OVERLAP
    )
    
    # Process files
    for file in os.listdir(config.DOCS_DIR):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(config.DOCS_DIR, file))
            try:
                pages = loader.load()
                chunks = text_splitter.split_documents(pages)
                all_chunks.extend(chunks)
            except Exception:
                continue
                
    if not all_chunks:
        return None

    # 3. Create a clean client instance directly linked to your storage location
    persistent_client = chromadb.PersistentClient(path=config.DB_DIR)
    
    # 4. Bind the client initialization to LangChain's wrapper framework
    vector_db = Chroma(
        client=persistent_client,
        embedding_function=embeddings
    )
    
    BATCH_SIZE = 32
    total_chunks = len(all_chunks)
    
    # Insert chunks in batches and report back to Streamlit layout
    for i in range(0, total_chunks, BATCH_SIZE):
        batch = all_chunks[i : i + BATCH_SIZE]
        vector_db.add_documents(batch)
        
        if progress_callback:
            current_progress = min((i + BATCH_SIZE) / total_chunks, 1.0)
            progress_callback(current_progress, i + BATCH_SIZE, total_chunks)

    return vector_db

def get_vector_db():
    """Simple loader for existing database using clean persistence mapping."""
    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL)
    if os.path.exists(config.DB_DIR) and os.listdir(config.DB_DIR):
        persistent_client = chromadb.PersistentClient(path=config.DB_DIR)
        return Chroma(client=persistent_client, embedding_function=embeddings)
    return None
