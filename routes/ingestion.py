import shutil
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from config.local_ai import get_embeddings, get_vector_store
from ingestion.ingest_documents import ingest_document

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    upload_dir = Path("data/raw_pdfs")
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_document(
        pdf_path=str(file_path),
        embeddings=get_embeddings(),
        vector_store_wrapper=get_vector_store()
    )

    return {
        "message": "Document uploaded and ingested successfully",
        "file_name": file.filename
    }