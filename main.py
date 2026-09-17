import os
from src import config, database, engine

def main():
    # Ensure directories exist
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    os.makedirs(config.DB_DIR, exist_ok=True)
    
    try:
        # Initialize database (loads existing or parses new PDFs)
        db = database.get_vector_db()
    except FileNotFoundError as e:
        print(f"\n[Error] {e}")
        return

    print("\n🚀 RAG Engine ready! Type your question below (or 'exit' to quit).")
    
    while True:
        user_query = input("\nAsk a question: ").strip()
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        if not user_query:
            continue
            
        print("Thinking...")
        response = engine.query_rag(db, user_query)
        print(f"\n[LLM Response]:\n{response}")

if __name__ == "__main__":
    main()
