import ollama
import json
from typing import List, Dict, Any

def generate_questions(
    chunk_text: str, 
    question_type: str, 
    char_limit: int, 
    model: str = "llama3.1:8b"
) -> List[Dict[str, Any]]:
    """
    Generates questions and answers from a text chunk using Ollama.
    """
    
    prompt = f"""
You are an expert educational content generator. Analyze the provided text and generate the maximum number of {question_type} questions.
    
    Focus on extracting:
    - Definitions
    - Comparisons
    - Timelines
    - Causes and Effects
    - Processes
    - Relationships
    - Important Concepts

    Constraints:
    1. The 'type' field must be '{question_type}'.
    2. Include a short 'context_snippet' from the text that supports the answer.
    3. Return ONLY a valid JSON list of objects.

    Output Schema:
    [
        {{
            "question": "The question text",
            "answer": "The answer text",
            "type": "{question_type}",
            "context_snippet": "Relevant text from source"
        }}
    ]
    """

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': f"Generate questions from this text:\n\n{chunk_text}"}
            ],
            format='json',
        )
        
        content = response['message']['content']
        data = json.loads(content)
        
        # Ensure it's a list (Ollama might sometimes return a dict wrapping the list)
        if isinstance(data, dict):
            # Try to find a list value if the root is a dict
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return [data] # Return the dict as a single item list if no list found
            
        return data

    except Exception as e:
        print(f"Error generating questions: {e}")
        return []
