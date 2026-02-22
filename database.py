import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")
SQLITE_URL = "sqlite:///./career_guidance.db"

_engine = None
_SessionLocal = None

def _connect():
    global _engine, _SessionLocal
    if _engine is None:
        url = DATABASE_URL
        is_sqlite = False
        
        if not url:
            print("⚠️ SUPABASE_DB_URL not found. Falling back to local SQLite.")
            url = SQLITE_URL
            is_sqlite = True
        
        try:
            connect_args = {"connect_timeout": 5} if not is_sqlite else {}
            # SQLite doesn't support pool_pre_ping in the same way, but it's safe to keep for Postgres
            _engine = create_engine(url, pool_pre_ping=is_sqlite is False, connect_args=connect_args)
            
            # Test connection
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            _SessionLocal = sessionmaker(bind=_engine)
            print(f"✅ Connected to {'Supabase' if not is_sqlite else 'Local SQLite'}")
        except Exception as e:
            if not is_sqlite:
                print(f"❌ Failed to connect to Supabase: {e}. Falling back to SQLite.")
                _engine = create_engine(SQLITE_URL)
                _SessionLocal = sessionmaker(bind=_engine)
                print("✅ Connected to Local SQLite")
            else:
                raise e
                
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
