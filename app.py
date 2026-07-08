import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from llm_chain import LegalLLMChain

st.set_page_config(page_title="Legal Document Assistant", layout="wide")

@st.cache_resource
def get_components():
    return DocumentProcessor(), VectorStoreManager(), LegalLLMChain()

doc_processor, vector_store_manager, llm_chain = get_components()

st.title("Legal Document Assistant ⚖️")
st.markdown("Upload a legal contract to ask questions about it. Answers are grounded purely in the document's text.")

if not os.environ.get("GROQ_API_KEY"):
    st.warning("Please set your GROQ_API_KEY in the .env file to use this app.")
    st.stop()

# Sidebar for file upload
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF or TXT contract", type=['pdf', 'txt'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Parsing and chunking document..."):
            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Extract Text
            if uploaded_file.name.endswith('.pdf'):
                pages_data = doc_processor.extract_text_from_pdf(tmp_file_path)
            else:
                # Handle TXT
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                # For txt, we just assume it's one long page
                pages_data = [{"page_num": 1, "text": text}]
                
            os.unlink(tmp_file_path)
            
            if not pages_data:
                st.error("Could not extract text from the document.")
            else:
                # Chunk and Embed
                chunks = doc_processor.chunk_text(pages_data, uploaded_file.name)
                st.info(f"Extracted and chunked into {len(chunks)} structural pieces.")
                
                with st.spinner("Building Vector Store..."):
                    vector_store_manager.create_vector_store(chunks)
                    st.session_state['doc_processed'] = True
                    st.session_state['doc_name'] = uploaded_file.name
                    st.success("Vector store built successfully!")

# Main chat area
if st.session_state.get('doc_processed', False):
    st.header("Ask a Question")
    question = st.text_input("Enter your question about the contract:")
    
    if st.button("Get Answer") and question:
        with st.spinner("Retrieving relevant clauses and generating answer..."):
            try:
                # 1. Retrieve top chunks
                retrieved_docs = vector_store_manager.retrieve(question, k=5)
                
                # 2. Generate answer
                answer = llm_chain.generate_answer(
                    question=question, 
                    docs=retrieved_docs, 
                    doc_name=st.session_state['doc_name']
                )
                
                # Display Answer
                st.subheader("Answer:")
                st.write(answer)
                
                # Display Sources
                with st.expander("View Source Excerpts"):
                    for i, doc in enumerate(retrieved_docs):
                        st.markdown(f"**[{i+1}] Page {doc.metadata.get('page_number', 'N/A')} - {doc.metadata.get('article', '')} {doc.metadata.get('section', '')}**")
                        st.text(doc.page_content)
                        
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("👈 Please upload and process a document to begin.")
