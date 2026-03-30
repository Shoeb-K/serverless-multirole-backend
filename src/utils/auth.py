import jwt
import hashlib
import os
import datetime

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-default-key-change-me")
JWT_ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 (simplified for serverless demo)."""
    # In a real prod environment, use bcrypt or passlib, but hashlib avoids native C dependencies in Lambda
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def generate_token(email: str, role: str) -> str:
    """Generates a JWT token valid for 24 hours."""
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decodes a JWT token. Raises Exception if invalid or expired."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def extract_token(headers: dict) -> str:
    """Extracts Bearer token from API Gateway headers."""
    if not headers:
        return None
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]
