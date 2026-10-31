import os
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from ingestion.pdf_to_markdown import PDFToMarkdownConverter
from ingestion.semantic_chunker import chunk_markdown
from rag.kpi_extractor_rag import extract_financial_metrics
from database.save_metrics import save_metrics

from vectorstore.azure_ai_search import (
    AzureAISearchVectorStore,
    Retriever as AzureSearchRetriever,
)
from vectorstore.chroma_store import (
    ChromaVectorStore,
    Retriever as ChromaRetriever,
)

# Load environment variables from a .env file
load_dotenv()


def parse_company_year(pdf_file: Path) -> Tuple[str, Optional[str]]:
    """Parse company name and year from a PDF filename."""
    stem = pdf_file.stem
    parts = stem.split("_")

    if parts and parts[0].isdigit():
        year = parts[0]
        company = parts[-1]
    elif len(parts) >= 2:
        company = parts[0]
        year = parts[1]
    else:
        company = stem
        year = None

    return company, year


def ingest_document(
    pdf_path: str,
    embeddings: Embeddings,
    vector_store_wrapper: ChromaVectorStore | AzureAISearchVectorStore
) -> None:
    """
    Ingest a PDF document, convert to markdown, chunk, store in vector DB,
    extract financial metrics, and save to PostgreSQL.
    """
    pdf_file = Path(pdf_path)

    try:
        # Step 1: Parse metadata (company and year) from filename
        company, year = parse_company_year(pdf_file)
        print(f"\n[Ingest] Processing {pdf_file.name} (Company: {company!r}, Year: {year!r})")

        # Step 2: Convert the PDF to Markdown format
        converter = PDFToMarkdownConverter()
        markdown_file = converter.convert_pdf(
            pdf_path=pdf_path,
            output_dir="data/markdown"
        )

        # Step 3: Chunk the markdown document semantically
        chunks = chunk_markdown(
            markdown_file=markdown_file,
            embeddings=embeddings
        )
        print(f"[Ingest] Generated {len(chunks)} chunks for {pdf_file.name}")

        # Step 4: Upload the text chunks into the configured vector store
        vector_store_wrapper.upload_chunks(
            chunks=chunks, 
            embeddings=embeddings,
            company=company,
            year=year,
            source_file=pdf_file.name
        )

        # Step 5: Instantiate the appropriate retriever
        if isinstance(vector_store_wrapper, AzureAISearchVectorStore):
            retriever = AzureSearchRetriever(vector_store_wrapper.client)
        else:
            chroma_store_instance = vector_store_wrapper.get_store(embeddings)
            retriever = ChromaRetriever(chroma_store_instance)

        # Step 6: Extract financial metrics using RAG
        parsed_year = int(year) if year and str(year).isdigit() else None
        metrics = extract_financial_metrics(
            retriever=retriever,
            company=company,
            year=parsed_year
        )

        # Step 7: Persist extracted metrics to the PostgreSQL database
        if metrics:
            save_metrics(
                company=company, 
                year=parsed_year, 
                metrics=metrics
            )
            print(f"[Success] Metrics saved for {company} ({year or 'N/A'})")
        else:
            print(f"[Warning] No metrics extracted for {pdf_file.name}")

    except Exception as e:
        print(f"[Error] Failed to ingest {pdf_file.name}: {str(e)}")


def ingest_directory(input_dir: str) -> None:
    """
    Ingest all PDFs from a directory using Hugging Face and ChromaDB.
    """
    print("Initializing Local HuggingFace Embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Initialize the Chroma Vector Store wrapper
    vector_store_wrapper = ChromaVectorStore(
        collection_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "financial-documents"),
        persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    )

    pdf_dir = Path(input_dir)
    if not pdf_dir.exists():
        print(f"[Error] Input directory '{input_dir}' does not exist.")
        return

    # Find all PDF files inside the input directory
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF(s) in {input_dir}")

    # Process each PDF file individually through the pipeline
    for pdf_file in pdf_files:
        ingest_document(
            pdf_path=str(pdf_file),
            embeddings=embeddings,
            vector_store_wrapper=vector_store_wrapper
        )


if __name__ == "__main__":
    ingest_directory("data/raw_pdfs")