from sqlalchemy import text

from database.postgres_sql import get_engine


def get_metrics():
    """Fetch the latest recorded financial metrics for each company and year from PostgreSQL."""
    engine = get_engine()

    # SQL query using Window Functions to fetch only the most recent entry per company and year
    query = """
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY company, year
                   ORDER BY created_at DESC
               ) AS rn
        FROM financial_metrics
    ) t
    WHERE rn = 1
    ORDER BY company
    """

    # Establish a connection, execute the query, and map the results into dictionaries
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = [dict(row._mapping) for row in result]

    return rows