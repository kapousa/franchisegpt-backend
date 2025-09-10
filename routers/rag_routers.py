from typing import List

from fastapi import APIRouter, Depends
from src.schemas.QueryRequest import QueryRequest
from src.schemas.PromptResponse import PromptResponse
from src.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["rag"])
rag_service = RAGService()

@router.post("/query", response_model=PromptResponse)
def query_rag(request: QueryRequest):
    context = rag_service.retrieve(request.query)
    answer = rag_service.generate_answer(request.query)
    return {"answer": answer, "context": context}

@router.post("/update-vectors")
async def update_vectors(docs: List[str]):
    """
    Admin updates the base vector DB with permanent docs.
    """
    rag_service.update_base_vectors(docs)
    return {"status": "success", "added_docs": len(docs)}