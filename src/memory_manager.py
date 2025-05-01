import os
import json
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_memory.json')


def load_memory():
    """Load all user-added memory notes from file."""
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
      content = f.read().strip()
      return json.loads(content) if content else []

def save_memory_entry(note):
    """Append a new note with timestamp to user memory."""
    memory = load_memory()
    memory.append({
        "timestamp": datetime.now().isoformat(),
        "entry": note.strip()
    })
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2)


def get_memory_documents():
    """Convert memory entries into RAG-friendly documents."""
    from langchain.docstore.document import Document
    memory = load_memory()
    return [Document(page_content=m["entry"], metadata={"source": "user_memory"}) for m in memory]
