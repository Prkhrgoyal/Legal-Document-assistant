import os
from typing import List
from langchain.schema import Document
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

class LegalLLMChain:
    def __init__(self, model_name="llama-3.1-8b-instant"):
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing.")
            
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=groq_api_key, 
            model_name=model_name
        )
        
        self.prompt = PromptTemplate.from_template(
            """You are a legal document assistant. You must answer the user's question
using ONLY the excerpts provided below, which come from the document
"{document_name}".

Rules:
1. If the excerpts do not contain enough information to answer the
   question, say so explicitly. Do not guess or use outside knowledge
   of general legal principles.
2. When you state a fact, note which excerpt (by number) it came from.
3. Do not provide legal advice or opinions — only report what the
   document states.
4. Keep your answer concise and directly responsive to the question.

Excerpts:
{context}

Question: {question}

Answer:"""
        )

    def format_docs(self, docs: List[Document]) -> str:
        formatted_excerpts = []
        for i, doc in enumerate(docs):
            page = doc.metadata.get("page_number", "Unknown")
            section = doc.metadata.get("section", "")
            article = doc.metadata.get("article", "")
            heading = f"{article} {section}".strip() or "General"
            
            excerpt = f"[{i+1}] (Section: {heading}, Page {page})\n{doc.page_content}\n"
            formatted_excerpts.append(excerpt)
        return "\n".join(formatted_excerpts)

    def generate_answer(self, question: str, docs: List[Document], doc_name: str) -> str:
        context = self.format_docs(docs)
        
        chain = self.prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "document_name": doc_name,
            "context": context,
            "question": question
        })
        
        return response
