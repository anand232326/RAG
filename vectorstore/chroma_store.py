import os
from langchain_chroma import Chroma
from langchain_core.documents import Document

class ChromaVectorStore:
    def __init__(self, collection_name: str = "financial-documents", persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None  # Will be initialized when embeddings are bound

    def get_store(self, embeddings):
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
        embeddings,
        company: str,
        year: str,
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
    """
    Adapter to match your existing Retriever(vector_store.client) pattern
    so your kpi_extractor_rag doesn't break.
    """
    def __init__(self, chroma_store):
        self.chroma_store = chroma_store

    def retrieve(self, query: str, company: str, year: int = None, k: int = 4):
        """
        Retrieve relevant chunks filtered by company and optional year.
        """
        filter_dict = {"company": company}
        if year:
            filter_dict["year"] = str(year)

        # Use Chroma's similarity search with metadata filtering
        results = self.chroma_store.similarity_search(
            query, 
            k=k, 
            filter=filter_dict
        )
        return results