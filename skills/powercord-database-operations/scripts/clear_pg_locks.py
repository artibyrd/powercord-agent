#!/usr/bin/env python3
"""Clear stale PostgreSQL locks and terminate hanging backend connections."""
import os
from sqlalchemy import create_engine, text

def main():
    db_url = os.environ.get(
        "POWERCORD_DATABASE_URL",
        "postgresql://powercord:test_pass@localhost:5433/powercord_dev"
    )
    print(f"Connecting to database to clear locks: {db_url}")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid()
              AND datname = current_database();
        """))
        print(f"Terminated idle/stale backend connections.")

if __name__ == "__main__":
    main()
