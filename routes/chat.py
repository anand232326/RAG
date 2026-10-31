from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.local_ai import create_chat_model, get_embeddings, get_vector_store
from vectorstore.chroma_store import Retriever

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    company: str | None = None
    year: int | None = None

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        vector_store = get_vector_store().get_store(get_embeddings())
        retriever = Retriever(vector_store)
        docs = retriever.retrieve(
            query=request.question,
            company=request.company,
            year=request.year
        )
        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = (
            "You are an expert financial analyst. Answer the user's question "
            "using only the context from corporate reports below. If the "
            "context is empty or does not contain the answer, say that there "
            "is not enough information.\n\n"
            f"Context:\n{context}\n\n"
            f"User Question: {request.question}\n\n"
            "Answer:"
        )

        response = create_chat_model().invoke(prompt)
        return {"answer": response.content}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Local RAG service failed: {e}") from e
