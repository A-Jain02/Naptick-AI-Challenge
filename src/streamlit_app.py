import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
import streamlit as st
from rag_pipeline import RAGPipeline
from memory_manager import save_memory_entry
import requests

# Setup page
st.set_page_config(page_title="SleepBot", page_icon="💌", layout="centered")
st.title("💌 SleepBot – AI Sleep Coach")
st.markdown("Ask me anything about your sleep, mood, wellness, or share how you're feeling.")

@st.cache_resource
def load_rag():
    rag = RAGPipeline()
    rag.load_vector_store()
    return rag

rag = load_rag()

# Memory input
st.markdown("---")
st.subheader("🧠 Add to Memory")
with st.form("memory_form", clear_on_submit=True):
    user_note = st.text_input("Tell me something about your day (e.g. 'I am anxious today'):")
    submitted = st.form_submit_button("Add to memory")
    if submitted and user_note.strip():
        save_memory_entry(user_note.strip())
        st.success("✅ Note saved! This will be considered in future answers.")

# Query input
st.subheader("💭 Ask a Question")
query = st.text_input("What would you like to know?")

# Ollama call
def call_ollama(prompt, model="mistral"):
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        return res.json().get("response", "").strip()
    except Exception:
        return "⚠️ Could not connect to Ollama. Is the model running?"

# Prompt formatter
def format_prompt(chunks, query):
    context = "\n".join([f"- {doc.page_content}" for doc in chunks])
    return f"""You are a sleep-focused assistant. Only use the information in the context below.

Context:
{context}

Only answer if the question can be answered using this context. If not, say: \"Sorry, I can't help with that.\"

Question: {query}
Answer:"""

# Run query
if query:
    with st.spinner("Thinking..."):
        results = rag.query(query, top_k=7)
        if not results:
            st.warning("Sorry, I couldn’t find anything relevant to that question.")
        else:
            prompt = format_prompt(results, query)
            answer = call_ollama(prompt)

            st.markdown("### 🧠 Answer")
            st.success(answer)

            with st.expander(" Retrieved Context"):
                for i, doc in enumerate(results):
                    st.markdown(f"**[{i+1}]** {doc.page_content}")
