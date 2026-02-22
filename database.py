import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

_engine = None
_SessionLocal = None


def _connect():
    global _engine, _SessionLocal
    if _engine is None:
        if not DATABASE_URL:
            raise ConnectionError(
                "❌ SUPABASE_DB_URL not found in .env file. "
                "Please set it to continue using database features."
            )
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 8})
        _SessionLocal = sessionmaker(bind=_engine)
    return _SessionLocal


class _LazySession:
    """A proxy that creates a real session only when first used."""
    def __init__(self):
        self._session = None

    def _get(self):
        if self._session is None:
            factory = _connect()
            self._session = factory()
        return self._session

    def execute(self, *args, **kwargs):
        return self._get().execute(*args, **kwargs)

    def commit(self):
        return self._get().commit()

    def rollback(self):
        if self._session:
            self._session.rollback()

    def close(self):
        if self._session:
            self._session.close()
            self._session = None


def SessionLocal():
    """Returns a lazy database session. Connection is deferred until first query."""
    return _LazySession()


def engine():
    _connect()
    return _engine
