from src.models.RAGModel import RAGModel
import os

rag = RAGModel(model="mistral")

# Loop through data folder and ingest files
data_folder = "data"
for file in os.listdir(data_folder):
    path = os.path.join(data_folder, file)
    if file.endswith(".txt"):
        rag.from_txt(path)
    elif file.endswith(".pdf"):
        rag.from_pdf(path)
    elif file.endswith(".docx"):
        rag.from_word(path)
    elif file.endswith(".xlsx"):
        rag.from_excel(path)
    elif file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
        rag.from_image(path)
    elif file.endswith(".mp3") or file.endswith(".wav"):
        rag.from_audio(path)

# Build vector index
rag.build_index()
