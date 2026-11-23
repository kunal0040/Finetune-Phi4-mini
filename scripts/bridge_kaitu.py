"""
bridge_kaitu.py
===============
Command-line bridge that sends a user query to phi4:mini-kaitu running in local Ollama,
passes the response through KaituOutputCleaner and KaituCommandGuard, and returns the result.
"""

import sys
import requests
from pathlib import Path

# Add scripts directory to path for guards
sys.path.insert(0, str(Path(__file__).parent))
from kaitu_safety_and_guard import KaituCommandGuard, KaituOutputCleaner, KaituMemory

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi4:mini-kaitu"

def query_kaitu(prompt: str, user_name: str = "Kunal") -> str:
    system_prompt = KaituMemory.format_system_prompt()
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 400
        }
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        raw_output = resp.json().get("message", {}).get("content", "")
    except Exception as e:
        return f"[Error connecting to Ollama {MODEL_NAME}]: {e}"

    # Apply Production Runtime Guards
    cleaned = KaituOutputCleaner.clean_response(prompt, raw_output)
    warnings = KaituCommandGuard.audit_text(cleaned)
    if warnings:
        cleaned += "\n\n⚠️ **Kaitu Safety Guard Notice:**\n" + "\n".join(f"- {w}" for w in warnings)

    return cleaned

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Hello Kaitu! Introduce yourself briefly."
    print(query_kaitu(query))
