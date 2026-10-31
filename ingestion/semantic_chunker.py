from pathlib import Path
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker
from dotenv import load_dotenv

# Load environment variables from a .env file (if any exist)
load_dotenv()


def read_markdown(markdown_file: str) -> str:
    """
    Read markdown content.

    Args:
        markdown_file: Markdown file path.

    Returns:
        Markdown content as a string.
    """
    return Path(markdown_file).read_text(encoding="utf-8")


def chunk_markdown(
    markdown_file: str,
    embeddings: Embeddings
) -> list[Document]:
    """
    Generate semantic chunks from markdown using Hugging Face embeddings.

    Args:
        markdown_file: Markdown file path.
        embeddings: Hugging Face embedding model instance.

    Returns:
        List of semantic chunks as LangChain Document objects.
    """
    # Read the raw markdown content from the file
    markdown_content = read_markdown(markdown_file)

    # Initialize the SemanticChunker with our Hugging Face embeddings and percentile threshold
    splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile"
    )

    # Split the text semantically and return as a list of Documents
    return splitter.create_documents([markdown_content])


if __name__ == "__main__":
    # Define the Hugging Face embedding model using a lightweight sentence-transformer
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Specify the target markdown file path
    markdown_file = "../data/markdown/2024_Apple.md"

    # Generate semantic chunks from the markdown document
    chunks = chunk_markdown(
        markdown_file=markdown_file,
        embeddings=embeddings
    )

    # Print total count of generated chunks
    print(f"Generated {len(chunks)} chunks\n")

    # Loop through and print the content of the first 3 chunks for preview
    for index, chunk in enumerate(chunks[:3]):
        print("=" * 80)
        print(f"Chunk {index + 1}")
        print("=" * 80)
        print(chunk.page_content[:1000])
        print()