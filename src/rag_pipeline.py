# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain.docstore.document import Document
# from data_loader import load_all_collections
# import os

# def prepare_documents():
#     """Loads and flattens relevant data into text chunks for embedding."""
#     data = load_all_collections()
#     text_chunks = []

#     for key in ["wearable_data", "wellness_notes", "mental_stress_tracker"]:
#         entries = data.get(key, [])
#         for entry in entries:
#             text_chunks.append(str(entry))  # convert dict to string

#     return [Document(page_content=chunk) for chunk in text_chunks]

# def build_vector_store(documents, persist_dir="rag_store"):
#     """Builds or loads a Chroma vector store from documents using HF embeddings."""
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     vectordb = Chroma.from_documents(documents, embeddings, persist_directory=persist_dir)
#     return vectordb

# def query_rag(vectordb, query, top_k=3):
#     """Returns top-k relevant document snippets from the vector store."""
#     results = vectordb.similarity_search(query, k=top_k)
#     return results

# # Test script
# if __name__ == "__main__":
#     docs = prepare_documents()
#     db = build_vector_store(docs)
#     query = "How was my stress level last week?"
#     results = query_rag(db, query)
#     for r in results:
#         print(r.page_content)

import os
from typing import List
from data_loader import load_all_collections

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class RAGPipeline:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_dir: str = "rag_store"
    ):
        """
        Initialize RAG Pipeline with embedding model and vector store path.
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
      data = load_all_collections()
      included_keys = ["wearable_data", "wellness_notes", "mental_stress_tracker"]

      all_chunks = set()  # deduplication via set
      documents = []

      for key in included_keys:
        entries = data.get(key, [])
        for entry in entries:
            raw_text = str(entry).strip()
            if raw_text not in all_chunks:
                all_chunks.add(raw_text)
                split_chunks = self.text_splitter.split_text(raw_text)
                for chunk in split_chunks:
                    documents.append(Document(page_content=chunk, metadata={"source": key}))

      print(f"✅ Prepared {len(documents)} unique text chunks for embedding.")
      return documents

    def build_vector_store(self, documents: List[Document]):
        """
        Create and persist a Chroma vector database from given documents.
        """
        print("⚙️ Building vector store...")
        self.vector_db = Chroma.from_documents(
            documents,
            self.embeddings,
            persist_directory=self.persist_dir
        )
        print("✅ Vector store created and persisted.")

    def load_vector_store(self):
        """
        Load an existing Chroma vector database from disk.
        """
        if not os.path.exists(self.persist_dir):
            raise FileNotFoundError(f"No vector store found at {self.persist_dir}.")
        print("📦 Loading existing vector store from disk...")
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )

    def query(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Perform semantic similarity search over the vector store.
        """
        if not self.vector_db:
            raise ValueError("Vector store is not initialized. Call build_vector_store() or load_vector_store() first.")
        print(f"🔍 Querying vector store: \"{query}\"")
        results = self.vector_db.similarity_search(query, k=top_k)
        print(f"📄 Retrieved {len(results)} relevant chunks.")
        return results


# Standalone script for testing
if __name__ == "__main__":
    rag = RAGPipeline()
    docs = rag.prepare_documents()
    rag.build_vector_store(docs)

    test_query = "I can't fall asleep easily."
    results = rag.query(test_query)

    for i, doc in enumerate(results):
      print(f"\n[{i+1}] Source: {doc.metadata.get('source')}")
      print(doc.page_content)


