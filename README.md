# RAG Legal Document Assistant ⚖️

A Retrieval-Augmented Generation (RAG) system specifically designed for legal contracts. This tool allows users to upload a contract (PDF or TXT) and ask questions about it. The system answers purely based on the provided document and strictly cites the sections and page numbers it used.

## 🎯 Why This Project Exists

Standard RAG implementations often fail on legal documents because they use fixed-length chunking (e.g., splitting every 500 tokens). This arbitrary splitting severs definitions from clauses and ruins legal meaning. 

This project implements a **Heading-Aware Structural Chunker** that reads the skeleton of the contract (Articles, Sections, Clauses) and chunks the text intelligently.

## ✨ Features
- **Heading-Aware Parsing:** Splits documents at semantic boundaries (`ARTICLE I`, `Section 1.2`, `(a)`) to preserve context.
- **Strict Anti-Hallucination Prompting:** The language model is heavily constrained to *only* answer using the provided excerpts or state that the document does not contain the answer.
- **Source Citations:** Every answer links directly back to the Section and Page Number of the original document.
- **Fast Local Retrieval:** Uses `sentence-transformers/all-MiniLM-L6-v2` and a fast, local FAISS vector store.
- **Streamlit Interface:** A clean, easy-to-use web UI.

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/rag-legal-assistant.git
cd rag-legal-assistant
```

### 2. Install dependencies
Ensure you have Python 3.8+ installed.
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
This project uses Groq's fast inference API for the Llama 3 model. You will need a free Groq API key.
* Rename `.env.example` to `.env`
* Add your API key:
```env
GROQ_API_KEY=your_api_key_here
```

### 4. Run the Application
```bash
streamlit run app.py
```

## 🏗️ Tech Stack
* **UI:** Streamlit
* **PDF Parsing:** pdfplumber
* **Chunking:** Custom Regex-based Structural Chunker
* **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
* **Vector Store:** FAISS
* **Orchestration:** LangChain
* **LLM:** Groq (Llama 3.1 8B)

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
