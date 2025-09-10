from typing import Optional, List, Dict
from fastapi import APIRouter, Form, File, UploadFile
from src.schemas.QueryRequest import QueryRequest
from src.schemas.PromptResponse import PromptResponse
from src.services.rag_service import RAGService
import json

router = APIRouter(prefix="/agent", tags=["agent"])
rag_service = RAGService()


@router.post("/ask")
async def user_query(
        query: str = Form(...),
        user_docs: Optional[List[UploadFile]] = File(None),
        save: bool = Form(True),
        chat_history: str = Form("[]")
):
    """
    User asks a question.
    - Can provide docs (user_docs).
    - Can choose to save them permanently (save=true).
    """
    try:
        parsed_history = json.loads(chat_history)
    except json.JSONDecodeError:
        parsed_history = []

    answer = await rag_service.answer_with_user_docs(
        query,
        user_docs=user_docs,
        save=save,
        chat_history=parsed_history
    )
    return {
        "query": query,
        "answer": answer,
        "used_user_docs": bool(user_docs),
        "saved_user_docs": save
    }