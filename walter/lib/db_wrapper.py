"""Simple SQLite wrapper to provide compatibility with the existing interface."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SimpleLiteWrapper:
    """A simple SQLite wrapper that provides the interface expected by Walter."""

    def __init__(self, db_path: str) -> None:
        """Initialize the database connection."""
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def init_database(self) -> None:
        """Initialize the database with required tables."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS project_tbl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            language TEXT NOT NULL,
            complete BOOLEAN NOT NULL DEFAULT 0
        )
        """
        self.cursor.execute(create_table_sql)
        self.connection.commit()

    def select(
        self, table: str, columns: List[str], where: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Select data from the database."""
        columns_str = "*" if "*" in columns else ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table}"
        if where:
            query += f" WHERE {where}"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def insert(self, table: str, columns: List[str], values: List[Any]) -> None:
        """Insert data into the database."""
        placeholders = ", ".join(["?"] * len(columns))
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        self.cursor.execute(query, values)
        self.connection.commit()

    def exists(self, table: str, where: str) -> bool:
        """Check if a record exists."""
        query = f"SELECT 1 FROM {table} WHERE {where} LIMIT 1"
        self.cursor.execute(query)
        return self.cursor.fetchone() is not None

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()

    def __del__(self) -> None:
        """Close the connection when the object is destroyed."""
        if hasattr(self, "connection"):
            self.connection.close()
