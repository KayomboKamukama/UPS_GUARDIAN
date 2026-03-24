"""SQLite data access utilities."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def connect(db_path: str) -> sqlite3.Connection:
    """Create SQLite connection with row factory."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn(db_path: str) -> Iterator[sqlite3.Connection]:
    """Yield an opened DB connection and ensure closure."""
    conn = connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_schema(db_path: str, schema_path: str) -> None:
    """Initialize database schema from SQL script file."""
    with get_conn(db_path) as conn:
        sql = Path(schema_path).read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()
