# app/auth/api_key_security.py
from passlib.context import CryptContext
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from config import get_sqlite_db_sync
from com.models.APIKey import APIKey
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)  # Look for 'X-API-Key' in headers


async def get_authorized_api_client(
        api_key: str = Security(api_key_header),
        db: Session = Depends(get_sqlite_db_sync)
) -> APIKey:
    """
    Dependency to validate the API key and return the APIKey object.
    This identifies the third-party application.
    """
    # In a real app, you would query your DB for an APIKey object
    # by its hashed key. This example simulates the lookup.
    # IMPORTANT: You must hash the incoming `api_key` and compare to the `key_hash` in your DB.
    # For simplicity here, let's assume a direct lookup for demonstration.
    # A more robust check might iterate through active keys and verify.

    # Example: A simplified, less efficient lookup (needs improvement for production)
    # Ideally, you'd perform a DB query based on a hash or a unique part of the key.
    # For now, let's assume you're fetching all active keys and verifying:
    all_active_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
    found_key_obj = None
    for k_obj in all_active_keys:
        if pwd_context.verify(api_key, k_obj.key_hash):  # Verify plain key against stored hash
            found_key_obj = k_obj
            break

    if not found_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
        )
    return found_key_obj


def api_key_permission_required(required_permissions: list[str]):
    """Higher-order dependency for permission-based authorization for API Clients."""

    async def permission_checker(
            api_client: APIKey = Depends(get_authorized_api_client)
    ):
        client_permissions = json.loads(api_client.permissions)  # Assuming permissions are stored as JSON string
        if not all(perm in client_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient API key permissions",
            )
        return api_client

    return permission_checker
