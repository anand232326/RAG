from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

class ChromaVectorStore:
    def __init__(self, collection_name: str = "financial-documents", persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None  # Will be initialized when embeddings are bound

    def get_store(self, embeddings: Embeddings) -> Chroma:
        """Returns the underlying LangChain Chroma instance."""
        store = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings,
            persist_directory=self.persist_directory
        )
        self.client = store  # Expose client/store for your custom Retriever if needed
        return store

    def upload_chunks(
        self,
        chunks: list[Document],
        embeddings: Embeddings,
        company: str,
        year: str | None,
        source_file: str
    ) -> None:
        """
        Upload chunks to ChromaDB, adding metadata for company, year, and source file.
        """
        store = self.get_store(embeddings)

        # Enhance chunks with metadata so you can filter by company/year later during RAG retrieval
        enriched_chunks = []
        for chunk in chunks:
            metadata = chunk.metadata.copy() if chunk.metadata else {}
            metadata.update({
                "company": company,
                "year": str(year),
                "source_file": source_file
            })
            enriched_chunks.append(
                Document(page_content=chunk.page_content, metadata=metadata)
            )

        print(f"Uploading {len(enriched_chunks)} chunks to ChromaDB...")
        store.add_documents(enriched_chunks)
        print("Upload complete.")


class Retriever:
    """Retrieve documents from a Chroma store with optional metadata filters."""

    def __init__(self, chroma_store: Chroma):
        self.chroma_store = chroma_store

    def retrieve(
        self,
        query: str,
        company: str | None = None,
        year: int | None = None,
        k: int = 4
    ) -> list[Document]:
        """Retrieve relevant chunks filtered by company and/or year."""
        conditions = []
        if company:
            conditions.append({"company": {"$eq": company}})
        if year is not None:
            conditions.append({"year": {"$eq": str(year)}})

        filters = None
        if len(conditions) == 1:
            filters = conditions[0]
        elif conditions:
            filters = {"$and": conditions}

        results = self.chroma_store.similarity_search(
            query,
            k=k,
            filter=filters
        )
        return results