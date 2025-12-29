import fitz  # PyMuPDF
from typing import List, Generator, Tuple

def extract_text_chunks(pdf_path: str, chunk_size: int = 3, overlap: int = 1) -> Generator[Tuple[str, int, int], None, None]:
    """
    Extracts text from a PDF using a sliding window approach.    
    Args:
        pdf_path: Path to the PDF file.
        chunk_size: Number of pages per chunk.
        overlap: Number of pages to overlap between chunks.        
    Yields:
        Tuple containing (combined_text, start_page_num, end_page_num).
        Page numbers are 1-based.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    # Calculate step size
    step = chunk_size - overlap
    if step < 1:
        step = 1

    for start_idx in range(0, total_pages, step):
        end_idx = min(start_idx + chunk_size, total_pages)
        
        # If we are at the end and the chunk is just the overlap from previous, stop 
        # (unless it's the very first chunk and total pages < chunk_size)
        if start_idx > 0 and start_idx >= total_pages:
            break

        chunk_text = []
        for i in range(start_idx, end_idx):
            page = doc.load_page(i)
            chunk_text.append(page.get_text())
        
        combined_text = "\n".join(chunk_text)
        
        # Adjust for 1-based indexing for display
        yield combined_text, start_idx + 1, end_idx

    doc.close()
