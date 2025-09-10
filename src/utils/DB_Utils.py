def hash_password(password: str) -> str:
    return f"hashed_{password}"

def verify_password(password: str, hashed: str) -> bool:
    return hashed == f"hashed_{password}"
