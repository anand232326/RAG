import os
import sys
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from vectorstore.chroma_store import ChromaVectorStore, Retriever

load_dotenv()


def search_vectorstore(query: str, top: int = 5):
    # Retrieve configuration from environment variables or use local defaults
    persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    collection_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "financial-documents")

    print(f"Initializing Local HuggingFace Embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    print(f"Connecting to ChromaDB at {persist_directory!r} (Collection: {collection_name!r})...")
    vector_store_wrapper = ChromaVectorStore(
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    # Get the underlying store and wrap it with the custom Retriever adapter
    chroma_store_instance = vector_store_wrapper.get_store(embeddings)
    retriever = Retriever(chroma_store_instance)

    # Perform similarity search using ChromaDB
    results = retriever.retrieve(
        query=query,
        company="",  # Empty string skips company filtering in debug mode unless specified
        year=None,   # None skips year filtering
        k=top
    )

    print(f"\nQuery: {query!r}")
    print(f"Top: {top}")
    print(f"Results found: {len(results)}\n")

    for idx, doc in enumerate(results, start=1):
        content = getattr(doc, "page_content", str(doc))

        snippet = content.strip().replace("\n", " ") if isinstance(content, str) else "<no content>"
        if len(snippet) > 350:
            snippet = snippet[:350].rstrip() + "..."

        print(f"Result {idx}")
        print(f"  Metadata: {getattr(doc, 'metadata', {})}")
        print(f"  Content snippet: {snippet}")
        print("  " + "-" * 60)

    if not results:
        print("No results returned. Verify your index/ChromaDB contents or try a different query.")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m rag.retrieval_debug \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    search_vectorstore(query)


if __name__ == "__main__":
    main()