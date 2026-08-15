#!/usr/bin/env python3
"""Inspect database tables and row counts in the Powercord PostgreSQL instance."""
import os
from sqlalchemy import create_engine, inspect, text

def main():
    db_url = os.environ.get(
        "POWERCORD_DATABASE_URL",
        "postgresql://powercord:test_pass@localhost:5433/powercord_dev"
    )
    print(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Found {len(tables)} tables:")
    with engine.connect() as conn:
        for t in sorted(tables):
            try:
                count = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
                print(f"  - {t}: {count} rows")
            except Exception as e:
                print(f"  - {t}: (error querying rows: {e})")

if __name__ == "__main__":
    main()
