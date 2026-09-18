import os
import pytest
from src.database import get_vector_db, rebuild_vector_db

# Mock document class to simulate PDF loader chunk data output structures
class DummyDoc:
    def __init__(self, content):
        self.page_content = content
        self.metadata = {"source": "test.pdf"}

def test_get_vector_db_returns_none_if_dir_empty(mocker):
    """Verifies that get_vector_db returns None if the DB directory is empty or missing."""
    mocker.patch("os.path.exists", return_value=False)
    assert get_vector_db() is None

def test_get_vector_db_successful_load(mocker):
    """Verifies get_vector_db initializes properly when storage files exist."""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.listdir", return_value=["data_file.bin"])
    mocker.patch("src.config.DB_DIR", "mock_db_dir")
    mocker.patch("src.config.EMBED_MODEL", "mock_model")

    mock_client = mocker.patch("chromadb.PersistentClient")
    mock_chroma = mocker.patch("src.database.Chroma", return_value="mocked_db_instance")
    mocker.patch("src.database.OllamaEmbeddings")

    db = get_vector_db()
    
    assert db == "mocked_db_instance"
    mock_client.assert_called_once_with(path="mock_db_dir")

def test_rebuild_vector_db_no_pdfs(mocker):
    """Verifies rebuild_vector_db exits cleanly if no PDFs exist to process."""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.listdir", return_value=[])  # Empty directory
    mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("src.database.OllamaEmbeddings")

    result = rebuild_vector_db()
    assert result is None

def test_rebuild_vector_db_successful_run(mocker):
    """Verifies the complete pipeline of rebuild_vector_db from parsing to batch loading."""
    # 1. Mock file system utilities safely
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    mocker.patch("chromadb.api.client.SharedSystemClient.clear_system_cache")
    
    # Simulate finding a single PDF in the documents folder
    mocker.patch("os.listdir", return_value=["sample.pdf"])
    
    # 2. Mock the Langchain document loaders directly at their origin library package namespace
    mock_loader_instance = mocker.Mock()
    mock_loader_instance.load.return_value = [DummyDoc("Raw text from PDF file.")]
    mock_loader_cls = mocker.patch(
        "langchain_community.document_loaders.PyPDFLoader", 
        return_value=mock_loader_instance
    )
    
    # 3. Mock the text splitting engine directly at its origin package namespace
    mock_splitter_instance = mocker.Mock()
    mock_splitter_instance.split_documents.return_value = [DummyDoc("Chunk 1 text")]
    mocker.patch(
        "langchain_text_splitters.RecursiveCharacterTextSplitter", 
        return_value=mock_splitter_instance
    )
    
    mocker.patch("src.database.OllamaEmbeddings")
    mocker.patch("chromadb.PersistentClient")
    
    # Mock Chroma collection instance and its add_documents method
    mock_chroma_instance = mocker.Mock()
    mocker.patch("src.database.Chroma", return_value=mock_chroma_instance)

    # Track progress callback tracking loops
    progress_calls = []
    def dummy_callback(progress, current, total):
        progress_calls.append(progress)

    # 4. Execute the pipeline
    db = rebuild_vector_db(progress_callback=dummy_callback)

    # 5. Asserts
    assert db == mock_chroma_instance
    mock_loader_cls.assert_called_once()
    mock_chroma_instance.add_documents.assert_called_once()
    assert len(progress_calls) == 1
    assert progress_calls == [1.0]
