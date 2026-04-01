"""
Database configuration for the household economics backend.

This module exposes a SQLAlchemy engine, session factory and a base class for
declarative models. The database URL is read from the ``DATABASE_URL``
environment variable if present. When unset the application defaults to
using a local SQLite database ``database.db`` in the working directory.

If a SQLite database is used, ``check_same_thread`` is disabled so that the
database can be accessed from different threads. This is a common pattern
when using SQLite with asynchronous frameworks such as FastAPI or
background tasks.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read the database URL from the environment or fall back to SQLite in the
# current directory. You can point this at PostgreSQL or another database
# by setting ``DATABASE_URL`` accordingly, e.g. ``postgresql://user:pass@host/db``.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Determine whether ``check_same_thread`` needs to be disabled. SQLite's
# default driver is not thread-safe but FastAPI will typically run in a
# multi-threaded environment. For non-SQLite drivers this flag is ignored.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create the SQLAlchemy engine. The ``future=True`` flag ensures that the
# newer 2.x engine interface is used consistently.
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)

# Create a configured ``Session`` class. Sessions are not threaded by default;
# each request should obtain a new session from this factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Base class for declarative models. All ORM models in this project should
# inherit from ``Base`` so that they are registered correctly with SQLAlchemy.
Base = declarative_base()

def init_db() -> None:
    """Create all tables in the database.

    This function should be called at application startup. SQLAlchemy will
    inspect all subclasses of ``Base`` and emit CREATE TABLE statements
    for any missing tables. If you change models you may need to handle
    migrations separately (e.g. with Alembic).
    """
    import economic_system.app.models  # noqa: F401 - imported for side effects
    Base.metadata.create_all(bind=engine)