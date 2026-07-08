from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

class VectorStoreManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.vector_store = None

    def create_vector_store(self, chunks: List[Dict[str, Any]]):
        """Converts chunks into LangChain Documents and builds FAISS index."""
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            )
            documents.append(doc)
        
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """Retrieves top-k similar documents for a given query."""
        if not self.vector_store:
            raise ValueError("Vector store has not been initialized. Please upload and process a document first.")
        
        return self.vector_store.similarity_search(query, k=k)
