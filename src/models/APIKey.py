import json
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from typing import List
from config import Base


class APIKey(Base):
    """SQLAlchemy model for API Keys."""
    __tablename__ = "api_key"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, unique=True, index=True, nullable=False)
    key_hash = Column(String, unique=True, nullable=False) # Store the hashed API key
    # Store permissions as a JSON string. Example: '["read_reports", "write_data"]'
    permissions_json = Column(String, nullable=False, default="[]")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) # Automatically update on record change

    # --- Instance Methods for Convenience ---

    @property
    def permissions(self) -> List[str]:
        """Returns the permissions as a list of strings."""
        if self.permissions_json:
            try:
                return json.loads(self.permissions_json)
            except json.JSONDecodeError:
                # Handle cases where permissions_json might be malformed
                return []
        return []

    def has_permission(self, permission: str) -> bool:
        """Checks if the API key has a specific permission."""
        return permission in self.permissions

    def has_all_permissions(self, required_permissions: List[str]) -> bool:
        """Checks if the API key has all the required permissions."""
        return all(perm in self.permissions for perm in required_permissions)

    def __repr__(self):
        return f"<APIKey(id={self.id}, client_name='{self.client_name}', is_active={self.is_active})>"
