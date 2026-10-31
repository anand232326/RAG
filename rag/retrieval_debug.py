import sys
from dotenv import load_dotenv

from config.local_ai import get_embeddings, get_vector_store
from vectorstore.chroma_store import Retriever

load_dotenv()


def search_vectorstore(query: str, top: int = 5):
    embeddings = get_embeddings()
    vector_store_wrapper = get_vector_store()

    chroma_store_instance = vector_store_wrapper.get_store(embeddings)
    retriever = Retriever(chroma_store_instance)

    results = retriever.retrieve(
        query=query,
        company=None,
        year=None,
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