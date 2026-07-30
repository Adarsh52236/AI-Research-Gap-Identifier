from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash_engine = PasswordHash((Argon2Hasher(),))

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hash_engine.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash using constant-time comparison."""
    return password_hash_engine.verify(password, password_hash)
