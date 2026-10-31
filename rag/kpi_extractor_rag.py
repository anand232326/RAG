import os
from collections.abc import Sequence
from typing import Protocol

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.documents import Document

from llm.azure_openai import get_structured_completion
from langchain_huggingface import HuggingFaceEmbeddings
from vectorstore.chroma_store import ChromaVectorStore, Retriever as ChromaRetriever

load_dotenv()

class RetrievedDocument(Protocol):
    page_content: str


class ContextRetriever(Protocol):
    def retrieve(
        self,
        query: str,
        company: str,
        year: int | None = None,
        k: int = 4
    ) -> Sequence[RetrievedDocument]: ...


class FinancialMetrics(BaseModel):
    revenue: str | int | None = Field(None, alias="Revenue")
    net_income: str | int | None = Field(None, alias="Net Income")
    operating_income: str | int | None = Field(None, alias="Operating Income")
    cash_flow: str | int | None = Field(None, alias="Cash Flow from Operating Activities")
    total_assets: str | int | None = Field(None, alias="Total Assets")
    total_liabilities: str | int | None = Field(None, alias="Total Liabilities")
    risk_factors: str | list | None = Field(None, alias="Top Risk Factors")
    growth_drivers: str | list | None = Field(None, alias="Top Growth Drivers")


def retrieve_context(
    retriever: ContextRetriever,
    company: str,
    year: int
) -> str:
    """
    Retrieve broad financial context from ChromaDB.
    """
    query = f"""
    Annual report financial statements,
    income statement,
    balance sheet,
    cash flow statement,
    risks,
    growth drivers,
    financial performance
    for {company} fiscal year {year}
    """

    # Retrieve matching LangChain Document objects from ChromaDB
    documents = retriever.retrieve(
        query=query,
        company=company,
        year=year,
        k=20
    )

    return "\n\n".join(
        doc.page_content
        for doc in documents
    )


def build_extraction_prompt(
    company: str,
    year: int,
    context: str
) -> str:
    """
    Build KPI extraction prompt.
    """
    return f"""
You are an expert financial analyst.

Company: {company}
Year: {year}

Context:
{context}

Extract the following information:

1. Revenue
2. Net Income
3. Operating Income
4. Cash Flow from Operating Activities
5. Total Assets
6. Total Liabilities
7. Top Risk Factors
8. Top Growth Drivers

Instructions:

- Use only the provided context.
- Return null if unavailable.
- Financial values must match the report exactly.
- Risk factors should be concise.
- Growth drivers should be concise.
- Return valid JSON only.
"""


def extract_financial_metrics(
    retriever: ContextRetriever,
    company: str,
    year: int
) -> dict:
    """
    Extract KPIs using RAG.
    """
    context = retrieve_context(
        retriever=retriever,
        company=company,
        year=year
    )

    prompt = build_extraction_prompt(
        company=company,
        year=year,
        context=context
    )

    metrics = get_structured_completion(
        prompt=prompt,
        response_model=FinancialMetrics
    )

    return metrics.model_dump()


def main() -> None:
    company = "Apple"
    year = 2024

    # 1. Initialize local HuggingFace Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # 2. Initialize ChromaDB Store wrapper
    vector_store_wrapper = ChromaVectorStore(
        collection_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "financial-documents"),
        persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    )

    # 3. Access underlying LangChain Chroma instance bound with embeddings
    chroma_instance = vector_store_wrapper.get_store(embeddings)

    # 4. Initialize local Chroma Retriever wrapper
    retriever = ChromaRetriever(chroma_instance)

    # 5. Extract metrics using RAG
    results = extract_financial_metrics(
        retriever=retriever,
        company=company,
        year=year
    )

    print(f"\nExtracted KPIs for {company} {year}\n")

    for key, value in results.items():
        print(f"{key}:")
        print(value)
        print("-" * 80)

    # 6. Save extracted metrics to database
    from database.save_metrics import save_metrics

    save_metrics(
        company=company,
        year=year,
        metrics=results
    )


if __name__ == "__main__":
    main()