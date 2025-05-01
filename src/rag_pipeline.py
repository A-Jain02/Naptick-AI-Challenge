import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
from typing import List
from data_loader import load_all_collections
from memory_manager import get_memory_documents

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class RAGPipeline:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_dir: str = "rag_store"
    ):
        """
        Initialize the RAG pipeline with embedding model and vector DB path.
        """
        self.persist_dir = persist_dir
        self.embedding_model = embedding_model
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self.vector_db = None

    def prepare_documents(self) -> List[Document]:
        """
        Load and flatten structured JSON data into Document objects.
        Includes persistent user memory.
        """
        data = load_all_collections()
        included_keys = ["wearable_data", "wellness_notes", "mental_stress_tracker"]

        seen_texts = set()
        documents = []

        # RAG chunks from data
        for key in included_keys:
            entries = data.get(key, [])
            for entry in entries:
                raw_text = str(entry).strip()
                if raw_text in seen_texts:
                    continue
                seen_texts.add(raw_text)

                chunks = self.text_splitter.split_text(raw_text)
                for chunk in chunks:
                    documents.append(Document(page_content=chunk, metadata={"source": key}))

        # Add memory documents directly (already chunked)
        memory_docs = get_memory_documents()
        documents.extend(memory_docs)

        print(f"✅ Prepared {len(documents)} total chunks (including memory).")
        return documents

    def build_vector_store(self, documents: List[Document]):
        """
        Create and persist a Chroma vector database from documents.
        """
        print("⚙️ Building vector store...")
        self.vector_db = Chroma.from_documents(
            documents,
            self.embeddings,
            persist_directory=self.persist_dir
        )
        print("✅ Vector store created at:", self.persist_dir)

    def load_vector_store(self):
        """
        Load an existing Chroma vector DB from disk.
        """
        if not os.path.exists(self.persist_dir):
            raise FileNotFoundError(f"No vector store found at {self.persist_dir}. Run build_vector_store first.")
        print("📦 Loading vector store...")
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )

    def query(self, query: str, top_k: int = 7) -> List[Document]:
        """
        Return top-k relevant documents using vector similarity search.
        """
        if not self.vector_db:
            raise ValueError("Vector store is not initialized.")
        print(f"🔍 Query: {query}")
        return self.vector_db.similarity_search(query, k=top_k)


# Standalone runner
if __name__ == "__main__":
    rag = RAGPipeline()
    docs = rag.prepare_documents()
    rag.build_vector_store(docs)

   #  sample_query = "What factors increased my stress last week?"
   #  results = rag.query(sample_query)

   #  for i, doc in enumerate(results, 1):
   #      print(f"\n--- Result {i} ---\n{doc.page_content}")
