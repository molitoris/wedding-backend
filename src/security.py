import secrets
import hashlib
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_token(length: int = 32):
    random_bytes = secrets.token_bytes(length)
    return random_bytes.hex()


def hash_token(input_string: str):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    hashed_string = sha256_hash.hexdigest()
    return hashed_string


def verify_token(clear_code: str, hashed_code: str) -> bool:
    return hash_token(clear_code) == hashed_code


def hash_password(input_string: str):
    return pwd_context.hash(input_string)


def verify_password(secret, hashed_password) -> bool:
    return pwd_context.verify(secret=secret, hash=hashed_password)
