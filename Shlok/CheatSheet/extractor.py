import ollama
from typing import Dict, Any
import json

SYSTEM_PROMPT = """
You are an expert knowledge extractor. Your task is to analyze the provided text from a document and extract structured information into JSON format.

Extract the following categories:
1. "definitions": A list of objects with "term" and "definition".
2. "comparisons": A list of objects with "subject_a", "subject_b", and "difference_or_similarity".
3. "timelines": A list of objects with "date" and "event".
4. "concepts": A list of objects with "name" and "explanation".

Rules:
- Output strictly valid JSON.
- If a category has no data, return an empty list for it.
- Be concise and accurate.
- Do not make up information.
"""

def extract_knowledge(text_chunk: str, model_name: str = "llama3.1:8b") -> Dict[str, Any]:
    """
    Sends text to Ollama and returns structured JSON extraction.
    """
    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f"Analyze this text and extract knowledge:\n\n{text_chunk}"}
            ],
            format='json',
        )
        
        content = response['message']['content']
        return json.loads(content)
        
    except Exception as e:
        print(f"Error extracting knowledge: {e}")
        return {
            "definitions": [],
            "comparisons": [],
            "timelines": [],
            "concepts": []
        }
