import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from flask import Flask, request, render_template
from google_fit_utils import fetch_steps_on_date
from rag_pipeline import RAGPipeline
from memory_manager import save_memory_entry
import requests
import re

app = Flask(__name__)

# Initialize RAG once
rag = RAGPipeline()
rag.load_vector_store()

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    if request.method == "POST":
        query = request.form.get("query", "").lower()

        if "step" in query:
            # Check if a date is mentioned
            match = re.search(r"on (\w+ \d{1,2}(?:, \d{4})?)", query)
            if match:
                date_str = match.group(1)
                steps = fetch_steps_on_date(date_str)
                if steps is not None:
                    answer = f"You took {steps} steps on {date_str}."
                else:
                    answer = f"Sorry, I couldn't understand the date '{date_str}'."
        else:
            retrieved_docs = rag.query(query, top_k=3)
            prompt = format_prompt(retrieved_docs, query)
            answer = call_ollama(prompt)

    return render_template("index.html", answer=answer)

def call_ollama(prompt, model="mistral"):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "").strip()
    except:
        return "⚠️ Could not connect to Ollama."

def format_prompt(chunks, query):
    context = "\n".join([f"- {doc.page_content}" for doc in chunks])
    return f"""You are a sleep-focused assistant. Use only the following context.

Context:
{context}

Only answer the question if relevant to the context. Otherwise say: \"Sorry, I can't help with that.\"

Question: {query}
Answer:"""

if __name__ == "__main__":
    app.run(debug=True, port=5050)
