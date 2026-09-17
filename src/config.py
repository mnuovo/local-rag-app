import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "uploaded_pdfs")
DB_DIR = os.path.join(BASE_DIR, "storage", "chroma_db")

LLM_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
