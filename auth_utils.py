import hashlib
import bcrypt

def _normalize_password(password: str) -> str:
    """
    Normalize password length using SHA-256
    to avoid bcrypt 72-byte limitation.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    normalized = _normalize_password(password)
    # bcrypt.hashpw returns bytes, so we decode it for storage
    return bcrypt.hashpw(normalized.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    normalized = _normalize_password(password)
    try:
        # bcrypt.checkpw expects both arguments as bytes
        return bcrypt.checkpw(normalized.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
