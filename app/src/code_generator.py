import secrets
import hashlib


def generate_code(length: int=32):
    random_bytes = secrets.token_bytes(length)
    return random_bytes.hex()

def hash_string(input_string: str):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    hashed_string = sha256_hash.hexdigest()
    return hashed_string

def check_code(clear_code: str, hashed_code: str) -> bool:
    return hash_string(clear_code) == hashed_code

if __name__ == '__main__':
    code = generate_code(8)
    print('r Code: ', code)
    hash = hash_string(code)
    print('f Hash:', hash_string(code))
    print('is valid:', check_code(code, hash))
