from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document

from config.local_ai import get_embeddings, get_vector_store


DEMO_RECORDS = [
    {
        "company": "Acme Solar",
        "year": "2024",
        "source_file": "acme_solar_2024_demo.txt",
        "content": (
            "Acme Solar 2024 annual report: Revenue was $125 million, up 25% "
            "from 2023. Net income was $18 million. The company generated "
            "420 gigawatt-hours of renewable electricity during the year."
        ),
    },
    {
        "company": "Acme Solar",
        "year": "2024",
        "source_file": "acme_solar_2024_demo.txt",
        "content": (
            "Acme Solar 2024 annual report risks: Delays in grid connections "
            "could postpone new projects. Higher interest rates may increase "
            "financing costs, and lower solar panel prices could reduce "
            "project returns."
        ),
    },
    {
        "company": "Acme Solar",
        "year": "2023",
        "source_file": "acme_solar_2023_demo.txt",
        "content": (
            "Acme Solar 2023 annual report: Revenue was $100 million and "
            "net income was $12 million. The company generated 350 "
            "gigawatt-hours of renewable electricity."
        ),
    },
    {
        "company": "Northstar Robotics",
        "year": "2024",
        "source_file": "northstar_robotics_2024_demo.txt",
        "content": (
            "Northstar Robotics 2024 annual report: Revenue was $80 million "
            "and net income was $9 million. The company shipped 2,400 "
            "warehouse robots and invested $7 million in research and "
            "development."
        ),
    },
]


def seed_demo_data() -> None:
    """Upsert synthetic report snippets into the configured Chroma collection."""
    documents = [
        Document(
            page_content=record["content"],
            metadata={
                "company": record["company"],
                "year": record["year"],
                "source_file": record["source_file"],
            },
        )
        for record in DEMO_RECORDS
    ]
    ids = [
        str(uuid5(NAMESPACE_URL, f"rag-demo:{record['source_file']}:{index}"))
        for index, record in enumerate(DEMO_RECORDS)
    ]

    store = get_vector_store().get_store(get_embeddings())
    store.add_documents(documents, ids=ids)
    print(f"Seeded {len(documents)} synthetic report snippets into Chroma.")


if __name__ == "__main__":
    seed_demo_data()
