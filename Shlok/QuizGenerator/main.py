import os
import json
import argparse
from tqdm import tqdm
from processor import extract_text_from_pdf, create_word_chunks
from llm_client import generate_questions

def get_user_input():
    print("--- PDF Question Generator Setup ---")
    pdf_path = input("Enter path to PDF file: ").strip()
    
    # Question Type
    print("\nSelect Question Type:")
    print("1. MCQ")
    print("2. True/False")
    print("3. Long Answer (Default)")
    q_choice = input("Choice (1-3): ").strip()
    
    q_type_map = {'1': 'MCQ', '2': 'True/False', '3': 'Long Answer'}
    question_type = q_type_map.get(q_choice, 'Long Answer')
    
    # Char Limit
    limit_input = input(f"\nEnter approximate character limit for answers (Default: 200): ").strip()
    char_limit = int(limit_input) if limit_input.isdigit() else 200
    
    return pdf_path, question_type, char_limit

def main():
    # Allow for optional command line args for automation, otherwise ask interactively
    parser = argparse.ArgumentParser(description="PDF QA Generator")
    parser.add_argument("--pdf", help="Path to PDF")
    parser.add_argument("--type", help="Question type (MCQ, True/False, Long Answer)")
    parser.add_argument("--limit", type=int, help="Character limit for answers")
    
    args = parser.parse_args()
    
    if args.pdf:
        pdf_path = args.pdf
        question_type = args.type if args.type else "Long Answer"
        char_limit = args.limit if args.limit else 200
    else:
        pdf_path, question_type, char_limit = get_user_input()

    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    print(f"\nProcessing '{pdf_path}'...")
    print(f"Settings: Type={question_type}, Limit={char_limit} chars")

    # 1. Extract and Chunk
    print("Extracting text and creating chunks...")
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        print("No text extracted.")
        return

    chunks = create_word_chunks(full_text, chunk_size=2500, overlap=100)
    print(f"Created {len(chunks)} chunks (2500 words each with overlap).")

    # 2. Generate Questions
    all_questions = []
    
    print("Generating questions with Llama 3.1...")
    for i, chunk in enumerate(tqdm(chunks, unit="chunk")):
        questions = generate_questions(chunk, question_type, char_limit)
        all_questions.extend(questions)

    # 3. Save Results
    output_file = "final_questions.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_questions, f, indent=4, ensure_ascii=False)
        print(f"\nSuccess! Generated {len(all_questions)} questions.")
        print(f"Saved to: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Error saving output: {e}")

if __name__ == "__main__":
    main()