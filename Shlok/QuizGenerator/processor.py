import fitz  # PyMuPDF
from typing import List

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def create_word_chunks(text: str, chunk_size: int = 2500, overlap: int = 100) -> List[str]:
    """
    Splits text into chunks of `chunk_size` words with `overlap` words.
    """
    words = text.split()
    chunks = []
    
    if not words:
        return []

    step = chunk_size - overlap
    if step < 1:
        step = 1

    for i in range(0, len(words), step):
        # Slice the list of words
        chunk_words = words[i : i + chunk_size]
        
        # Join back into a string
        chunk_str = " ".join(chunk_words)
        chunks.append(chunk_str)
        
        # Break if we've reached the end of the text
        if i + chunk_size >= len(words):
            break
            
    return chunks
