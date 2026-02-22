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
        url = DATABASE_URL
        
        if not url:
            raise ValueError("SUPABASE_DB_URL not found in environment variables.")
        
        try:
            # Use connection pooling and timeout for Postgres
            _engine = create_engine(
                url, 
                pool_pre_ping=True, 
                connect_args={"connect_timeout": 10}
            )
            
            # Test connection immediately
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            _SessionLocal = sessionmaker(bind=_engine)
            print("Connected to Supabase (Postgres)")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to connect to Supabase: {e}")
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

    def get_bind(self, *args, **kwargs):
        return self._get().get_bind(*args, **kwargs)

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
