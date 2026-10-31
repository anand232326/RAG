import os
from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from vectorstore.chroma_store import ChromaVectorStore


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    return HuggingFaceEmbeddings(
        model_name=os.getenv(
            "HUGGINGFACE_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
    )


@lru_cache(maxsize=1)
def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(
        collection_name=os.getenv(
            "CHROMA_COLLECTION_NAME",
            "financial-documents"
        ),
        persist_directory=os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            "./chroma_db"
        )
    )


def create_chat_model(*, format: str | dict | None = None) -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
        format=format
    )
