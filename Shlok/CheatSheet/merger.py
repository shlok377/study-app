from typing import List, Dict, Any

def merge_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges multiple extraction dictionaries into a single master dictionary,
    removing duplicates.
    """
    merged = {
        "definitions": {},  # Keyed by term
        "comparisons": set(), # Set of tuples for uniqueness
        "timelines": {},    # Keyed by date+event signature
        "concepts": {}      # Keyed by concept name
    }

    for res in results:
        # 1. Merge Definitions (Deduplicate by Term)
        for item in res.get("definitions", []):
            term = item.get("term", "").strip()
            if term and term not in merged["definitions"]:
                merged["definitions"][term] = item["definition"]

        # 2. Merge Comparisons (Deduplicate by full content)
        for item in res.get("comparisons", []):
            # Create a hashable representation
            comp_tuple = (
                item.get("subject_a", "").strip(),
                item.get("subject_b", "").strip(),
                item.get("difference_or_similarity", "").strip()
            )
            merged["comparisons"].add(comp_tuple)

        # 3. Merge Timelines (Deduplicate by Date + Event)
        for item in res.get("timelines", []):
            date_str = item.get("date", "").strip()
            event_str = item.get("event", "").strip()
            key = f"{date_str}||{event_str}"
            if key and key not in merged["timelines"]:
                merged["timelines"][key] = item

        # 4. Merge Concepts (Deduplicate by Name)
        for item in res.get("concepts", []):
            name = item.get("name", "").strip()
            if name and name not in merged["concepts"]:
                merged["concepts"][name] = item["explanation"]

    # Convert back to list format
    final_output = {
        "definitions": [
            {"term": k, "definition": v} for k, v in merged["definitions"].items()
        ],
        "comparisons": [
            {"subject_a": t[0], "subject_b": t[1], "difference_or_similarity": t[2]} 
            for t in merged["comparisons"]
        ],
        "timelines": list(merged["timelines"].values()),
        "concepts": [
            {"name": k, "explanation": v} for k, v in merged["concepts"].items()
        ]
    }
    
    # Sort for tidiness (Optional)
    final_output["definitions"].sort(key=lambda x: x["term"])
    final_output["timelines"].sort(key=lambda x: x["date"])
    final_output["concepts"].sort(key=lambda x: x["name"])

    return final_output
