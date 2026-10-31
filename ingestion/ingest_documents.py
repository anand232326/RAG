from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv

from langchain_core.embeddings import Embeddings

from config.local_ai import get_embeddings, get_vector_store
from ingestion.pdf_to_markdown import PDFToMarkdownConverter
from ingestion.semantic_chunker import chunk_markdown
from rag.kpi_extractor_rag import extract_financial_metrics
from database.save_metrics import save_metrics

from vectorstore.chroma_store import ChromaVectorStore, Retriever

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
    vector_store_wrapper: ChromaVectorStore
) -> None:
    """
    Ingest a PDF document, convert to markdown, chunk, store in vector DB,
    extract financial metrics, and save to PostgreSQL.
    """
    pdf_file = Path(pdf_path)

    company, year = parse_company_year(pdf_file)
    print(f"\n[Ingest] Processing {pdf_file.name} (Company: {company!r}, Year: {year!r})")

    converter = PDFToMarkdownConverter()
    markdown_file = converter.convert_pdf(
        pdf_path=pdf_path,
        output_dir="data/markdown"
    )

    chunks = chunk_markdown(
        markdown_file=markdown_file,
        embeddings=embeddings
    )
    print(f"[Ingest] Generated {len(chunks)} chunks for {pdf_file.name}")

    vector_store_wrapper.upload_chunks(
        chunks=chunks,
        embeddings=embeddings,
        company=company,
        year=year,
        source_file=pdf_file.name
    )

    parsed_year = int(year) if year and year.isdigit() else None
    retriever = Retriever(vector_store_wrapper.get_store(embeddings))
    metrics = extract_financial_metrics(
        retriever=retriever,
        company=company,
        year=parsed_year,
        report_text=Path(markdown_file).read_text(encoding="utf-8")
    )

    if metrics:
        save_metrics(
            company=company,
            year=parsed_year,
            metrics=metrics
        )
        print(f"[Success] Metrics saved for {company} ({year or 'N/A'})")
    else:
        print(f"[Warning] No metrics extracted for {pdf_file.name}")


def ingest_directory(input_dir: str) -> None:
    """
    Ingest all PDFs from a directory using Hugging Face and ChromaDB.
    """
    embeddings = get_embeddings()
    vector_store_wrapper = get_vector_store()

    pdf_dir = Path(input_dir)
    if not pdf_dir.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist.")

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