from flask import Flask, render_template, request
from rag_pipeline import RAGPipeline
from google_fit_utils import fetch_steps_on_date
from app import format_prompt, call_ollama  # adjust this import as needed
import re

app = Flask(__name__)
rag = RAGPipeline()
rag.load_vector_store()

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    if request.method == "POST":
        query = request.form.get("query", "").lower()

        if "step" in query:
            match = re.search(r"on ([a-zA-Z0-9 ,]+)", query)
            if match:
                date_str = match.group(1)
                steps = fetch_steps_on_date(date_str)
                if steps is not None:
                    answer = f"You took {steps} steps on {date_str.strip()}."
                else:
                    answer = f"Sorry, I couldn't understand the date '{date_str.strip()}'."
            else:
                answer = "Please specify a date, e.g., 'steps on April 25'."
        else:
            retrieved_docs = rag.query(query, top_k=3)
            prompt = format_prompt(retrieved_docs, query)
            answer = call_ollama(prompt)

    return render_template("index.html", answer=answer)