from sqlalchemy import text

from database.postgres_sql import get_engine, create_database


def create_tables() -> None:
    """Create the financial_metrics table in PostgreSQL if it doesn't already exist."""
    engine = get_engine()

    query = """
    CREATE TABLE IF NOT EXISTS financial_metrics (
        id SERIAL PRIMARY KEY,
        company VARCHAR(100),
        year VARCHAR(10),
        revenue TEXT,
        net_income TEXT,
        operating_income TEXT,
        cash_flow TEXT,
        total_assets TEXT,
        total_liabilities TEXT,
        risk_factors TEXT,
        growth_drivers TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # Establish a safe transactional connection and execute the SQL query
    with engine.begin() as connection:
        connection.execute(text(query))

    print("financial_metrics table created.")


if __name__ == "__main__":
    # Ensure the database exists before trying to create tables inside it
    create_database()
    create_tables()