import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def _normalize_password(password: str) -> str:
    """
    Normalize password length using SHA-256
    to avoid bcrypt 72-byte limitation.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    normalized = _normalize_password(password)
    return pwd_context.hash(normalized)

def verify_password(password: str, hashed: str) -> bool:
    normalized = _normalize_password(password)
    return pwd_context.verify(normalized, hashed)
