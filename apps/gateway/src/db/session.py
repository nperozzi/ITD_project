"""SQLAlchemy engine + session factory.

Constructed once and injected into repositories via the DI container. Repositories
receive the session factory, not a session, so they can open short-lived sessions
per call without sharing state across coroutines.
"""

from __future__ import annotations

from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


SessionFactory = Callable[[], Session]


def build_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine.

    SQLite needs `check_same_thread=False` so callbacks on different threads
    (e.g. paho-mqtt, bleak) can share it safely through short-lived sessions.
    """

    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, future=True, connect_args=connect_args)


def build_session_factory(engine: Engine) -> SessionFactory:
    """Create a thread-safe session factory bound to the given engine."""

    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
