from __future__ import annotations

from contextlib import contextmanager

from flask import current_app


@contextmanager
def session_scope():
    db = current_app.config.get("db")
    if db is None:
        raise RuntimeError("Database is not configured for this app.")

    with db.SessionLocal() as session:
        yield session
