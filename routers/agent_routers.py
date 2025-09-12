from typing import Optional, List, Dict
from fastapi import APIRouter, Form, File, UploadFile, Request
from src.schemas.QueryRequest import QueryRequest
from src.schemas.PromptResponse import PromptResponse
from src.services.rag_service import RAGService
import json

router = APIRouter(prefix="/agent", tags=["agent"])
rag_service = RAGService()


@router.post("/ask")
async def user_query(request: Request):
    """
    User asks a question.
    - Can provide docs (user_docs).
    - Can choose to save them permanently (save=true).
    """
    try:
        form_data = await request.form()
        query = form_data.get("query", "")
        save = form_data.get("save", "true").lower() == "true"
        chat_history_str = form_data.get("chat_history", "[]")

        try:
            parsed_history = json.loads(chat_history_str)
        except json.JSONDecodeError:
            parsed_history = []

        user_docs = form_data.getlist("user_docs")

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
    except Exception as e:
        # A more detailed error response can be helpful for debugging
        return {"error": str(e)}, 500