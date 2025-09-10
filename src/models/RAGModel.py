import os
import sqlite3

import faiss
import pandas as pd
import pytesseract
import requests
import whisper
from PIL import Image
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from docx import Document
from sentence_transformers import SentenceTransformer


class RAGModel:
    def __init__(self, vector_db_path="vector.index", model="mistral"):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.vector_db_path = vector_db_path
        self.text_chunks = []
        self.index = None
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"

    # ---------- Data ingestion ----------
    def from_txt(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            self.text_chunks.append(f.read())

    def from_pdf(self, filepath):
        reader = PdfReader(filepath)
        text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        self.text_chunks.append(text)

    def from_word(self, filepath):
        doc = Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
        self.text_chunks.append(text)

    def from_excel(self, filepath):
        df = pd.read_excel(filepath)
        text = df.astype(str).apply(lambda x: " ".join(x), axis=1).tolist()
        self.text_chunks.extend(text)

    def from_db(self, db_path, query):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(query, conn)
        text = df.astype(str).apply(lambda x: " ".join(x), axis=1).tolist()
        self.text_chunks.extend(text)

    def from_web(self, url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        self.text_chunks.append(soup.get_text())

    def from_image(self, filepath):
        text = pytesseract.image_to_string(Image.open(filepath))
        self.text_chunks.append(text)

    def from_audio(self, filepath):
        model = whisper.load_model("base")
        result = model.transcribe(filepath)
        self.text_chunks.append(result["text"])

    # ---------- Embedding & Index ----------
    def build_index(self):
        if not self.text_chunks:
            raise ValueError("No data ingested. Add data first.")
        embeddings = self.embedder.encode(self.text_chunks, convert_to_numpy=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        faiss.write_index(self.index, self.vector_db_path)
        print(f"✅ Vector index saved to {self.vector_db_path}")

    def load_index(self):
        if os.path.exists(self.vector_db_path):
            self.index = faiss.read_index(self.vector_db_path)
            print("✅ Loaded existing vector index")
        else:
            raise FileNotFoundError("No index found. Build index first.")

    # ---------- Retrieval ----------
    def retrieve(self, query, top_k=3):
        if self.index is None:
            self.load_index()
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        D, I = self.index.search(q_emb, top_k)
        results = [self.text_chunks[i] for i in I[0]]
        return results

    # ---------- RAG Answer Generation ----------
    def ask(self, query, top_k=3):
        context_docs = self.retrieve(query, top_k)
        context_text = "\n\n".join(context_docs)
        prompt = f"Answer the question using the following context:\n{context_text}\n\nQuestion: {query}\nAnswer:"

        payload = {"model": self.model, "prompt": prompt}
        response = requests.post(self.ollama_url, json=payload, stream=True)

        answer = ""
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if '"response":"' in data:
                    part = data.split('"response":"')[1].split('"')[0]
                    answer += part

        return {"query": query, "answer": answer, "sources": context_docs}
