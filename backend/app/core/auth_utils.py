import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from backend.app.config import settings
import logging
logger = logging.getLogger(__name__)

# Monkeypatch passlib bcrypt bug with bcrypt 4.x
try:
    import passlib.handlers.bcrypt
    import bcrypt
    if not hasattr(bcrypt, "__about__"):
        class About:
            __version__ = bcrypt.__version__
        bcrypt.__about__ = About
    
    # Monkeypatch bcrypt.hashpw to prevent passlib's 255-byte self-test from crashing
    # bcrypt >= 4.0.0. User passwords > 72 bytes are already blocked by the API.
    _original_hashpw = bcrypt.hashpw
    def _safe_hashpw(password, salt):
        return _original_hashpw(password[:72], salt)
    bcrypt.hashpw = _safe_hashpw
except ImportError:
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "supersecretkey_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def password_too_long(password: str) -> bool:
    return len(password.encode("utf-8")) > 72

def verify_password_safe(plain_password, hashed_password):
    try:
        if password_too_long(plain_password):
            return False
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
