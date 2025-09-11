from pydantic import BaseModel, Field # Import Field for default_factory
from typing import Optional, List # Import List for type hinting lists

# --- Common Base Schema ---
class UserBase(BaseModel):
    username: str
    email: str # Or EmailStr if you enable it and have validation
    # Remove the single 'role: str' as it's replaced by 'roles: List[str]'
    avatar: Optional[str] = None # Assuming avatar can be optional

# --- Schema for User Creation (input) ---
class UserCreate(UserBase):
    password: str
    # When creating, allow specifying roles as a list
    # Use default_factory for mutable defaults (empty list)
    roles: List[str] = Field(default_factory=list)


# --- Schema for User Response (output) ---
class User(UserBase):
    id: str # Assuming user IDs are strings (like UUIDs)
    # Add roles as a list of strings
    roles: List[str] = Field(default_factory=list) # Ensure roles are included in the response

    class Config:
        # Pydantic v2 uses `from_attributes = True`
        from_attributes = True
        # Pydantic v1 used `from_attributes = True`
        # from_attributes = True


# --- Token Response Schema ---
class Token(BaseModel):
    access_token: str
    token_type: str


# --- Token Payload Data (What's in the JWT payload and decoded) ---
class TokenData(BaseModel):
    username: Optional[str] = None
    # Crucially, update this to be a list of roles
    roles: List[str] = Field(default_factory=list) # Default to an empty list if no roles are in payload