from src.services.rag_service import RAGService

def test_generate_answer():
    rag = RAGService()
    answer = rag.generate_answer("What is FastAPI?")
    assert "Answer generated" in answer
