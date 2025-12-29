import argparse
import sys
import json
import os
from tqdm import tqdm
from pdf_processor import extract_text_chunks
from extractor import extract_knowledge
from merger import merge_results

def main():
    parser = argparse.ArgumentParser(description="PDF Knowledge Extractor using Ollama (Llama 3.1)")
    parser.add_argument("pdf_path", help="Path to the source PDF file")
    parser.add_argument("--output", "-o", default="output.json", help="Path to save the final JSON output")
    parser.add_argument("--model", "-m", default="llama3.1:8b", help="Ollama model to use")
    
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found: {args.pdf_path}")
        sys.exit(1)

    print(f"Processing {args.pdf_path}...")
    print(f"Using model: {args.model}")

    # 1. Parse PDF into chunks
    # We collect all chunks first to know the total for tqdm, 
    # or we can just iterate. Let's collect to be safe and simple.
    print("Reading PDF and creating chunks...")
    chunks = list(extract_text_chunks(args.pdf_path))
    print(f"Total chunks created: {len(chunks)}")

    # 2. Extract Knowledge from each chunk
    extracted_data = []
    
    print("Extracting knowledge (this may take a while)...")
    for text, start, end in tqdm(chunks, unit="chunk"):
        result = extract_knowledge(text, model_name=args.model)
        extracted_data.append(result)

    # 3. Merge Results
    print("Merging and deduplicating results...")
    final_knowledge = merge_results(extracted_data)

    # 4. Save to file
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(final_knowledge, f, indent=4, ensure_ascii=False)
        print(f"Success! Knowledge extracted to {args.output}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
