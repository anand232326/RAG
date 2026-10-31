import os
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from langchain_openai import AzureOpenAIEmbeddings
from vectorstore.azure_ai_search import AzureAISearchVectorStore
from ingestion.ingest_documents import ingest_document

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        upload_dir = Path("data/raw_pdfs")
        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = upload_dir / file.filename

        # 1. Save the uploaded file to disk securely
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Initialize embeddings configuration
        embeddings = AzureOpenAIEmbeddings(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )

        # 3. Initialize Azure AI Search vector store wrapper
        vector_store = AzureAISearchVectorStore(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            api_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
        )

        # 4. Trigger document ingestion pipeline
        ingest_document(
            pdf_path=str(file_path),
            embeddings=embeddings,
            vector_store_wrapper=vector_store
        )

        return {
            "message": "Document uploaded and ingested successfully",
            "file_name": file.filename
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during ingestion: {str(e)}"
        )