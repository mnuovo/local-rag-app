# 🗺️ Local Doc AI - Development Roadmap

This document outlines the planned improvements, features, and architectural upgrades for the local Retrieval-Augmented Generation (RAG) application running on Apple Silicon (M1 Pro).

---

## 📈 Phase 1: Context & Intelligence Upgrades (Short-Term)
*Focus: Enhancing retrieval precision and keeping track of conversation flow.*

*   **Hybrid Search Integration (Lexical + Semantic)**
    *   *Goal:* Combine ChromaDB's vector search (conceptual meaning) with traditional BM25 keyword matching.
    *   *Why:* Ensures perfect accuracy when searching for exact code variables, class annotations (e.g., `@SpringBootApplication`), or function names.
*   **Contextual Re-ranking (Rerankers)**
    *   *Goal:* Retrieve a larger initial pool of document fragments (e.g., $k=15$) and pass them through a lightweight local re-ranking model like `FlashRank`.
    *   *Why:* Filters context down to the absolute most relevant top 5 chunks, minimizing LLM confusion and reducing prompt token overhead.
*   **Conversational Chat Memory Window**
    *   *Goal:* Implement a memory buffer that attaches the last 3-4 conversational turns back into the local Ollama context window for every query.
    *   *Why:* Allows you to ask conversational follow-up questions seamlessly (e.g., *"Can you give me an example of the pattern you just explained?"*).

---

## 🎨 Phase 2: User Experience & Asset Workspace (Medium-Term)
*Focus: Abstracting manual terminal configurations into a unified frontend cockpit.*

*   **Dynamic UI Document Manager Sidebar**
    *   *Goal:* Build a visual interactive sidebar checklist inside Streamlit showcasing all currently indexed textbook volumes.
    *   *Why:* Allows you to see exactly what knowledge bases are active and easily toggle specific files on or off before executing a query.
*   **Native Drag-and-Drop File Upload Web Widget**
    *   *Goal:* Integrate an automated upload element (`st.file_uploader`) to handle PDF parsing and batching in the background.
    *   *Why:* Eliminates the need to open Finder, navigate to the `uploaded_pdfs` directory, or run database flush commands (`rm -rf storage/chroma_db`) via a separate terminal loop.
*   **Multi-Format Document Ingestion Engine**
    *   *Goal:* Broaden the python loading pipeline (`src/database.py`) to process Markdown (`.md`), plain text (`.txt`), Word (`.docx`), and code repositories (`.java`).
    *   *Why:* Expands your personal AI research assistant beyond textbooks into raw software code repositories.

---

## ⚡ Phase 3: Advanced Architecture & Speed Tuning (Long-Term)
*Focus: Moving towards high-efficiency infrastructure layouts and multi-modal understanding.*

*   **Multimodal Visual RAG Pipeline**
    *   *Goal:* Swap out `pypdf` for a layout-aware vision parser (e.g., `LlamaParse`) and target a multimodal vision-enabled LLM (`llama3.2-vision`).
    *   *Why:* Enables the AI to read, extract, and fully explain complex technical charts, object interaction diagrams, and architectural layout graphics embedded inside textbooks.
*   **Docker Containerization**
    *   *Goal:* Package the application workspace, python virtual environment flags, database schemas, and system files into an isolated Docker network.
    *   *Why:* Guarantees a 1-click deployment configuration on any machine or local server environment without manual Python installation dependencies.
*   **Automated Verification & Evaluation Framework**
    *   *Goal:* Tie an evaluation toolkit (such as `Ragas` or `TruLens`) into your workflow.
    *   *Why:* Provides actionable mathematical metrics scoring your application's absolute answer correctness, background truthfulness, and retrieval efficiency as you experiment with different chunk sizes.
