import os
import pytest
from src.engine import prepare_rag_payload

# Create a minimal mock class to simulate langchain's Document objects
class MockDocument:
    def __init__(self, page_content, source_path, page_num=None):
        self.page_content = page_content
        # Emulate the nested structure of langchain document metadata
        self.metadata = {"source": source_path}
        if page_num is not None:
            self.metadata["page"] = page_num

def test_prepare_rag_payload_with_pages():
    """Tests payload generation when source documents include specific page numbers."""
    # 1. Setup mock retrieved documents
    mock_docs = [
        MockDocument("Artificial intelligence is broad.", "/docs/ai_overview.pdf", page_num=0),
        MockDocument("RAG improves LLM context accuracy.", "/docs/rag_deep_dive.pdf", page_num=4)
    ]
    
    # 2. Mock the vector database similarity search function
    class MockVectorDB:
        def similarity_search(self, query, k):
            return mock_docs

    db = MockVectorDB()
    query = "What is RAG?"
    
    # 3. Call the actual function under test
    prompt, sources = prepare_rag_payload(db, query)
    
    # 4. Asserts (Verifications)
    # Check that contents are formatted inside the prompt pool
    assert "Artificial intelligence is broad." in prompt
    assert "RAG improves LLM context accuracy." in prompt
    assert "QUESTION:\nWhat is RAG?" in prompt
    
    # Check that sources were cleanly extracted and page increments are correct (+1)
    assert len(sources) == 2
    assert "📖 ai_overview.pdf (Page 1)" in sources
    assert "📖 rag_deep_dive.pdf (Page 5)" in sources

def test_prepare_rag_payload_without_pages():
    """Tests payload generation gracefully handles documents missing page metadata."""
    mock_docs = [
        MockDocument("Some textual data fragment.", "/docs/web_scrape.txt", page_num=None)
    ]
    
    class MockVectorDB:
        def similarity_search(self, query, k):
            return mock_docs

    db = MockVectorDB()
    prompt, sources = prepare_rag_payload(db, "Test query")
    
    # Verify parsing didn't attempt to append empty "(Page None)" strings
    assert len(sources) == 1
    assert "📖 web_scrape.txt" in sources
