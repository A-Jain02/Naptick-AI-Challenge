import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, render_template
from rag_pipeline import RAGPipeline
from memory_manager import save_memory_entry
import requests

app = Flask(__name__)

# Initialize RAG once
rag = RAGPipeline()
rag.load_vector_store()

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    context_docs = []

    if request.method == "POST":
        user_query = request.form.get("query", "").strip()
        user_note = request.form.get("note", "").strip()

        if user_note:
            save_memory_entry(user_note)

        if user_query:
            results = rag.query(user_query, top_k=5)
            context_docs = [doc.page_content for doc in results]
            prompt = format_prompt(results, user_query)
            answer = call_ollama(prompt)

    return render_template("index.html", answer=answer, context=context_docs)

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
