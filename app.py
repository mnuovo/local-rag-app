import os
import streamlit as st
from src import database, engine, config

# 1. Page Browser Configurations
st.set_page_config(page_title="Local Doc AI", page_icon="📚", layout="centered")
st.title("📚 Local Doc AI")
st.caption("Powered entirely offline by Ollama (Llama 3.2) & ChromaDB")

# 2. Inject WhatsApp-style alignment CSS
st.markdown("""
<style>
    div[data-testid="stChatMessage"]:has(.user-hook) {
        display: flex !important;
        flex-direction: row-reverse !important;
        justify-content: flex-start !important;
        text-align: right !important;
        width: 100% !important;
    }
    div[data-testid="stChatMessage"]:has(.user-hook) [data-testid="stChatMessageContent"] {
        flex-grow: 0 !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    div[data-testid="stChatMessage"]:has(.user-hook) .stMarkdown {
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# Ensure folders exist
os.makedirs(config.DOCS_DIR, exist_ok=True)

# ==========================================
# 🛠️ SIDEBAR MANAGEMENT WIDGET
# ==========================================
with st.sidebar:
    st.header("📂 Document Workspace")
    
    # Render Active Inventory at the top
    st.subheader("📚 Active Library Inventory:")
    active_docs = [f for f in os.listdir(config.DOCS_DIR) if f.endswith(".pdf")]
    if active_docs:
        for doc in active_docs:
            st.write(f"📎 `{doc}`")
    else:
        st.caption("No documents loaded yet.")
        
    st.write("---")

    # 1. Initialize an uploader key tracker in memory if it doesn't exist
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    # 2. File Uploader UI Component linked to our dynamic key identifier
    uploaded_files = st.file_uploader(
        "Upload new PDF textbooks:", 
        type=["pdf"], 
        accept_multiple_files=True,
        key=f"pdf_uploader_{st.session_state.uploader_key}" # <-- Tied to state key
    )
    
    if st.button("🔄 Sync & Re-index Library", use_container_width=True):
        if uploaded_files:
            # Write newly uploaded streams to the disk
            for uploaded_file in uploaded_files:
                file_path = os.path.join(config.DOCS_DIR, uploaded_file.name)
                if not os.path.exists(file_path):
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
            
            st.info("Rebuilding index with your documents... Please wait.")
            ui_progress_bar = st.progress(0.0)
            ui_status_text = st.empty()
            
            def update_ui_progress(pct, indexed, total):
                ui_progress_bar.progress(pct)
                ui_status_text.text(f"Embedded {indexed}/{total} text fragments...")
            
            # Rebuild vector blocks
            updated_db = database.rebuild_vector_db(progress_callback=update_ui_progress)
            
            if updated_db:
                st.success("Indexing Complete! Refreshing application...")
                st.cache_resource.clear()  
                
                # 3. 💡 THE FIX: Advance the key counter before reloading!
                # Changing this key forces Streamlit to destroy the old upload box and draw a completely clean empty one.
                st.session_state.uploader_key += 1
                
                st.rerun()
        else:
            st.warning("Please upload at least one PDF file first.")

# ==========================================
# 🧠 DATABASE INITIALIZATION
# ==========================================
@st.cache_resource
def load_system_db():
    return database.get_vector_db()

# 1. First, check if there are actually any physical PDFs in the directory
pdf_files_in_folder = [f for f in os.listdir(config.DOCS_DIR) if f.endswith(".pdf")]

if not pdf_files_in_folder:
    # If the folder is empty, warn the user and stop execution before showing the green box
    st.warning("⚠️ Your document library is currently empty. Please upload some PDF files into the sidebar on the left and click 'Sync & Re-index' to begin!", icon="ℹ️")
    st.stop()

# 2. If files exist, try loading the vector database
db = load_system_db()

if db is None:
    # If files exist on disk but the database hasn't been built yet
    st.info("💡 Your PDF files are uploaded but not indexed yet. Please click 'Sync & Re-index Library' in the sidebar to build your local AI brain!", icon="⚙️")
    st.stop()
else:
    # ONLY show this green success banner if files exist AND the database is successfully built
    st.success("Vector Engine Active & Documents Synchronized!", icon="✅")

# ==========================================
# 💬 CHAT INTERFACE LOOP
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"<span class='user-hook'></span>{message['content']}", unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

if user_query := st.chat_input("Ask a question about your books..."):
    with st.chat_message("user"):
        st.markdown(f"<span class='user-hook'></span>{user_query}", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        prompt, sources = engine.prepare_rag_payload(db, user_query)
        
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=config.LLM_MODEL)
        
        for chunk in llm.stream(prompt):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
            
        if sources:
            full_response += "\n\n---\n**Sources used from your library:**"
            for source in sources:
                full_response += f"\n* {source}"
                
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
