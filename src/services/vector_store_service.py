import os
import uuid
from typing import List, Optional, Dict
from chromadb import PersistentClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Ensure persistence directory exists
os.makedirs(CHROMA_DB_DIR, exist_ok=True)


class VectorStoreService:
    def __init__(self, collection_name: str = "documents"):
        """
        Initialize ChromaDB client and embedding model.
        """
        # Use PersistentClient for disk persistence
        self.chroma_client = PersistentClient(path=CHROMA_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "RAG documents collection"}
        )
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    def add_to_vectorstore(
        self,
        docs: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None,
        chunk_size: int = 100
    ):
        """
        Add documents to vector store.
        - Generates UUIDs if IDs are not provided
        - Allows optional metadata for each doc
        - Supports batching for large document lists
        """
        if not docs:
            return 0

        ids = ids or [str(uuid.uuid4()) for _ in docs]
        metadatas = metadatas or [{"source": "default"} for _ in docs]

        total_added = 0
        for i in range(0, len(docs), chunk_size):
            batch_docs = docs[i:i + chunk_size]
            batch_ids = ids[i:i + chunk_size]
            batch_metadata = metadatas[i:i + chunk_size]

            embeddings = self.embedding_model.encode(batch_docs).tolist()
            self.collection.add(
                documents=batch_docs,
                embeddings=embeddings,
                ids=batch_ids,
                metadatas=batch_metadata
            )
            total_added += len(batch_docs)

        return total_added

    def search_vectors(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search the most relevant documents for a query.
        Returns a list of dicts with id, text, metadata, and distance score.
        """
        query_embedding = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        formatted = []
        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "id": results["ids"][0][i],
                "text": doc,
                "metadata": results.get("metadatas", [{}])[0][i],
                "score": results["distances"][0][i]
            })
        return formatted

    def upsert_vector(
        self,
        doc: str,
        id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add or update a single document in the vector store.
        """
        vector_id = id or str(uuid.uuid4())
        meta = metadata or {}
        embedding = self.embedding_model.encode([doc]).tolist()
        self.collection.upsert(
            documents=[doc],
            embeddings=embedding,
            ids=[vector_id],
            metadatas=[meta]
        )
        return vector_id

    def delete_vector(self, id: str):
        """
        Remove a document from the vector store by ID.
        """
        self.collection.delete(ids=[id])
