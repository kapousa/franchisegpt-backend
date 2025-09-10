import json
import os
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.services.vector_store_service import VectorStoreService

SAMPLE_DIR = "sample_data"
vector_store_service = VectorStoreService()

# Text splitter config
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

class DataService:

    def __init__(self):
        pass

    def load_text_file(self, filepath):
        """Load and split a plain text file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            chunks = splitter.split_text(text)
            ids = [str(uuid.uuid4()) for _ in chunks]
            vector_store_service.add_to_vectorstore(chunks, ids)
            print(f"✅ Loaded {filepath} with {len(chunks)} chunks")
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}")

    def load_json_file(self, filepath):
        """Load and split JSON file with text fields."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            chunks = []
            for entry in data:
                if isinstance(entry, dict):
                    # Pick the text fields (adjust if needed)
                    text = " ".join(str(v) for v in entry.values() if isinstance(v, str))
                    if text:
                        chunks.extend(splitter.split_text(text))

            ids = [str(uuid.uuid4()) for _ in chunks]
            vector_store_service.add_to_vectorstore(chunks, ids)
            print(f"✅ Loaded {filepath} with {len(chunks)} chunks")
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}")


if __name__ == "__main__":
    data_service = DataService()
    sample_files = [
        "wikipedia.txt",
        "faq.txt",
        "franchise.txt",
        "franchise_data.json"
    ]

    for file in sample_files:
        file_path = os.path.join(SAMPLE_DIR, file)  # always look inside sample_data/
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue

        if file.endswith(".json"):
            data_service.load_json_file(file_path)
        else:
            data_service.load_text_file(file_path)

    # Debugging: check how many vectors we have
    try:
        print("📊 Vector store count:", vector_store_service.collection.count())
    except Exception as e:
        print(f"⚠️ Could not fetch vector store count: {e}")
