from fastapi import APIRouter
from src.services.vector_store_service import VectorStoreService

router= APIRouter(prefix="/data", tags=["data"])
vector_store = VectorStoreService()

@router.get("/list-vectors")
def list_vectors():
    collection = vector_store.collection
    docs = [{"id": i, "text": t} for i, t in zip(collection.get()["ids"], collection.get()["documents"])]
    return {"documents": docs}
