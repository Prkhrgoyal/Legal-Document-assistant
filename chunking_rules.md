# Chunking Rules for Legal Contracts (Based on CUAD)

When processing legal documents for a Retrieval-Augmented Generation (RAG) system, standard fixed-length chunking (e.g., splitting every 500 tokens) will break clauses in half and sever context. Based on an analysis of the CUAD (Contract Understanding Atticus Dataset) text files, we must implement a **heading-aware, structural chunker**.

Here are the rules to follow when parsing and chunking these documents:

## 1. Top-Level Boundaries (Articles & Main Sections)
Legal contracts are structured hierarchically. The chunker must first identify major structural boundaries.
*   **Articles:** Look for patterns like `ARTICLE I`, `ARTICLE II`, `ARTICLE VIII CONFIDENTIALITY`. These denote major topic shifts.
*   **Main Sections:** Look for numbered sections like `1. Services.`, `2. Compensation.`, `3. Termination.`.
*   **Special Sections:** Look for standard standalone sections like `RECITALS`, `AGREEMENT`, `IN WITNESS WHEREOF`.

**Rule:** A chunk should never cross a top-level boundary. A new Article or Main Section always starts a new chunk.

## 2. Mid-Level Boundaries (Subsections)
Main sections can often be too long for a language model's context window or a vector embedding limit.
*   **Numbered Subsections:** Look for patterns like `1.1 Provision of Services.`, `1.2 Standard of Service.`, `7.1 Further Assurances.`.
*   **Rule:** If a Main Section exceeds the target chunk size (e.g., 400-500 tokens), split it at these mid-level subsection boundaries.

## 3. Low-Level Boundaries (Paragraphs & Clauses)
If a subsection is still too long, we must split it further using semantic markers rather than arbitrary character counts.
*   **Lettered/Numbered Clauses:** Look for `(a)`, `(b)`, `(c)`, or `(i)`, `(ii)`. These often represent a list of conditions or obligations.
*   **Rule:** Split at these clause markers.

## 4. Fallback: Sentence-Level Splitting
If a single, continuous paragraph (with no subsections or lettered clauses) exceeds the token limit, fall back to sentence-level splitting.
*   **Rule:** Use a sentence tokenizer (like `nltk.sent_tokenize` or `spacy`) to split the text. Ensure that the split occurs at a period `.`, and maintain an overlap of 1-2 sentences (approx. 50-100 tokens) to preserve the context between chunks.

## 5. Exhibits and Schedules
Contracts often include appendices at the end.
*   **Markers:** Look for `EXHIBIT A`, `EXHIBIT B`, `SCHEDULE 1`.
*   **Rule:** Treat Exhibits and Schedules as completely separate top-level boundaries. Do not merge the text of an Exhibit with the signature block or the preceding section.

## 6. Page Numbers and Footers
The OCR or text extraction process often leaves page numbers (e.g., standalone lines with just `2`, `3`, `4`) and recurring footers.
*   **Rule:** Before chunking, run a pre-processing step to strip out standalone page numbers and repetitive footer text, but log the page number so it can be added to the chunk's metadata. 

## 7. Metadata Enrichment
A chunk is useless without knowing where it came from.
*   **Rule:** Every chunk must be accompanied by metadata indicating its lineage. 
    *   `document_name`
    *   `page_number` (if available from PDF parsing)
    *   `parent_article` (e.g., "ARTICLE VIII")
    *   `section_header` (e.g., "8.01 Confidentiality")

## Summary of the Chunking Hierarchy
1. Attempt to chunk by **Articles / Main Sections**.
2. If > Max Tokens, chunk by **Subsections** (`1.1`, `1.2`).
3. If > Max Tokens, chunk by **Clauses** (`(a)`, `(b)`).
4. If > Max Tokens, chunk by **Sentences** (with overlap).
