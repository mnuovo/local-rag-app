import os
import pytest
from main import main

def test_main_successful_flow(mocker):
    """Tests that main() creates directories, runs a query, and exits properly."""
    
    # 1. Mock the configurations to use dummy paths during the test
    mocker.patch("src.config.DOCS_DIR", "mock_docs_dir")
    mocker.patch("src.config.DB_DIR", "mock_db_dir")
    
    # 2. Mock os.makedirs so it doesn't actually touch your real local hard drive
    mock_makedirs = mocker.patch("os.makedirs")
    
    # 3. Mock the database initialization so it just returns a dummy string
    mock_db = "dummy_vector_db_object"
    mock_get_db = mocker.patch("src.database.get_vector_db", return_value=mock_db)
    
    # 4. Mock the LLM RAG engine to return a fixed test response
    mock_query_rag = mocker.patch("main.engine.query_rag", return_value="This is a test response.", create=True)
    
    # 5. Simulate user input: first they ask a question, then they type 'exit'
    mocker.patch("builtins.input", side_effect=["What is AI?", "exit"])
    
    # 6. Mock print so we don't clutter the terminal logs during testing
    mock_print = mocker.patch("builtins.print")
    
    # Execute the actual main function under these simulated conditions
    main()
    
    # --- VERIFICATIONS (Asserts) ---
    # Check that directories were requested to be made
    mock_makedirs.assert_any_call("mock_docs_dir", exist_ok=True)
    mock_makedirs.assert_any_call("mock_db_dir", exist_ok=True)
    
    # Check that the vector database was initialized
    mock_get_db.assert_called_once()
    
    # Check that the engine was called with our dummy db and the user's question
    mock_query_rag.assert_called_once_with(mock_db, "What is AI?")
    
    # Check that the script printed the final goodbye message before terminating
    mock_print.assert_any_call("Goodbye!")


def test_main_database_not_found(mocker):
    """Tests that main() catches a missing database error and exits gracefully."""
    
    mocker.patch("os.makedirs")
    
    # Simulate the database failing to initialize with a FileNotFoundError
    mocker.patch("src.database.get_vector_db", side_effect=FileNotFoundError("Missing files"))
    
    mock_print = mocker.patch("builtins.print")
    
    # Execute main - it should catch the error internally and return instead of crashing
    main()
    
    # Verify the error was printed to the user gracefully
    mock_print.assert_any_call("\n[Error] Missing files")
