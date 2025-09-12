# src/services/rag_service.py
import os
from typing import List, Optional, Dict
from fastapi import UploadFile
from dotenv import load_dotenv
from src.services.ollama_service import OllamaService
from src.services.vector_store_service import VectorStoreService

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
ALLOWED_KEYWORDS = ["franchise", "franchising", "royalty", "franchise fee", "brand expansion", "territory", "franchise agreement"]


class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.ollama = OllamaService()

    def update_base_vectors(self, docs: List[str]):
        added_count = self.vector_store.add_to_vectorstore(docs)
        return {"added_docs": added_count}

    async def _rephrase_query(self, query: str, chat_history: List[Dict]) -> str:
        """Uses the LLM to rephrase a follow-up question into a standalone query."""
        if not chat_history:
            return query

        history_prompt = ""
        for msg in chat_history:
            history_prompt += f"{msg['sender'].capitalize()}: {msg['content']}\n"

        rephrase_prompt = f"""Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question. This standalone question can then be used to perform a relevant search.

Conversation History:
{history_prompt}

Follow-up Question: {query}

Standalone Question:"""

        rephrased_query = self.ollama.generate_answer(rephrase_prompt)
        # ADD THIS PRINT STATEMENT
        print(f"DEBUG: Rephrased Query is: '{rephrased_query.strip()}'")
        return rephrased_query.strip()

    async def answer_with_user_docs(
            self,
            query: str,
            user_docs: Optional[List[UploadFile]] = None,
            save: bool = True,
            top_k: int = 3,
            chat_history: Optional[List[Dict]] = None
    ) -> str:
        extra_docs_content: List[str] = []
        if user_docs:
            for doc in user_docs:
                content_bytes = await doc.read()
                content_str = content_bytes.decode("utf-8", errors="ignore")
                extra_docs_content.append(content_str)

        # Step 1: Rephrase the query to a standalone question using the chat history
        standalone_query = await self._rephrase_query(query, chat_history)

        # Step 2: Perform the vector search using the rephrased query
        retrieved_docs = self.vector_store.search_vectors(standalone_query, top_k=top_k)
        context_parts = [doc["text"] for doc in retrieved_docs]

        if extra_docs_content:
            context_parts.extend(extra_docs_content)

        context_text = "\n\n".join(context_parts)

        if context_text:
            # Step 3: Use the original chat history and retrieved documents to generate the final answer
            history_prompt = ""
            if chat_history:
                for msg in chat_history:
                    history_prompt += f"{msg['sender'].capitalize()}: {msg['content']}\n"

            prompt = f"""You are a helpful assistant. Here is the previous conversation history:
            {history_prompt}

            As a Franchise Consultant, you ONLY answer questions related to franchises, franchising, and business consulting.  
            If the user asks something unrelated (e.g., about health, travel, coding, or personal topics), respond with exactly:
            "I'm only specialized in giving franchise consulting answers."

            Context:
            {context_text}

            Question:
            {query}"""

            answer = self.ollama.generate_answer(prompt)

            if save and extra_docs_content:
                self.vector_store.add_to_vectorstore(extra_docs_content)
        else:
            answer = "Sorry, as a Franchise Consultant, your question is not within my scope."

        return answer