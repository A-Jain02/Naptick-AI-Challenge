import requests
from rag_pipeline import RAGPipeline

# Initialize RAG
rag = RAGPipeline()
try:
    rag.load_vector_store()
except Exception as e:
    print("❌ Vector store not found. Please run rag_pipeline.py first.")
    exit()

# Call local Ollama model
def call_ollama(prompt, model="mistral"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        return "⚠️ Failed to connect to Ollama. Is the model running?"

# Prompt builder
def format_prompt(chunks, query):
    context = "\n".join([f"- {doc.page_content}" for doc in chunks])
    return f"""You are a sleep-focused assistant that must answer strictly based on the provided context.

Context:
{context}

Only answer the question if it can be answered using this context. If not, respond with exactly: "Sorry, I can’t help with that."

Question: {query}
Answer:"""

# CLI loop
print("\n🤖 SleepBot (Ollama-Mistral) is ready! Type your question (or 'exit'):\n")
while True:
    query = input("You: ").strip()
    if query.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    retrieved_docs = rag.query(query, top_k=7)
    if not retrieved_docs:
        print("\n🧠 Sorry, I couldn’t find anything relevant to that question.\n")
        continue

    prompt = format_prompt(retrieved_docs, query)
    response = call_ollama(prompt)
    print(f"\n🧠 Answer: {response}\n")

