from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from config import settings


@contextmanager
def get_db_connection(autocommit: bool = False) -> Iterator[psycopg.Connection]:
    connection = psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)
    connection.autocommit = autocommit
    try:
        yield connection
        if not autocommit:
            connection.commit()
    except Exception:
        if not autocommit:
            connection.rollback()
        raise
    finally:
        connection.close()
