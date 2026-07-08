import re
import pdfplumber
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self):
        # Regex patterns for structural boundaries
        # Matches: ARTICLE I, ARTICLE 1, Article II, etc.
        self.article_pattern = re.compile(r'^(?:ARTICLE|SECTION)\s+[IVX\d]+\b', re.IGNORECASE)
        # Matches: 1. Services., 2. Compensation.
        self.main_section_pattern = re.compile(r'^\d+\.\s+[A-Z]')
        # Matches: 1.1, 1.2.
        self.sub_section_pattern = re.compile(r'^\d+\.\d+\.?\s+')
        # Matches: EXHIBIT A, SCHEDULE 1
        self.exhibit_pattern = re.compile(r'^(?:EXHIBIT|SCHEDULE)\s+[A-Z\d]+', re.IGNORECASE)

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extracts text from PDF page by page, keeping page numbers."""
        pages_data = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        pages_data.append({"page_num": i + 1, "text": text})
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return pages_data

    def chunk_text(self, pages_data: List[Dict[str, Any]], doc_name: str) -> List[Dict[str, Any]]:
        """
        Implements heading-aware chunking.
        Returns a list of chunks with metadata.
        """
        chunks = []
        current_chunk_text = []
        current_article = "Preamble"
        current_section = ""
        current_page = 1
        
        def save_chunk():
            if current_chunk_text:
                text = "\n".join(current_chunk_text).strip()
                if text:
                    chunks.append({
                        "text": text,
                        "metadata": {
                            "document_name": doc_name,
                            "page_number": current_page,
                            "article": current_article,
                            "section": current_section
                        }
                    })
                current_chunk_text.clear()

        for page in pages_data:
            current_page = page['page_num']
            lines = page['text'].split('\n')
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Check for page numbers / standalone footers to ignore
                if line_stripped.isdigit() and len(line_stripped) < 4:
                    continue

                # Check for top-level boundaries
                if self.article_pattern.match(line_stripped) or self.exhibit_pattern.match(line_stripped):
                    save_chunk()
                    current_article = line_stripped
                    current_section = ""
                    current_chunk_text.append(line_stripped)
                # Check for main sections
                elif self.main_section_pattern.match(line_stripped):
                    save_chunk()
                    current_section = line_stripped
                    current_chunk_text.append(line_stripped)
                # Check for subsections (if current chunk is getting long, split)
                elif self.sub_section_pattern.match(line_stripped) and len(" ".join(current_chunk_text).split()) > 200:
                    save_chunk()
                    current_chunk_text.append(line_stripped)
                else:
                    current_chunk_text.append(line_stripped)
                    
                # Hard fallback for extremely long blocks (e.g. > 400 words)
                if len(" ".join(current_chunk_text).split()) > 400:
                    save_chunk()
                    
        save_chunk() # Save the last chunk
        return chunks
