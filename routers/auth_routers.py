from fastapi import APIRouter, HTTPException, Depends
from src.schemas.User import User
from src.services.auth.jwt_security import get_current_user
from src.utils.DB_Utils import hash_password, verify_password
from src.services.auth_service import AuthService
from src.services.db_service import DBService

router = APIRouter(prefix="/auth", tags=["auth"])
db = DBService()

@router.get("/verify")
def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """
    Verifies the user's authentication token.
    This endpoint is called by the frontend's ProtectedRoute component.
    The `Depends(get_current_user)` function handles all token validation.
    If the token is valid, the function returns a success message.
    If the token is invalid or missing, `get_current_user` will automatically
    raise an HTTPException (401 Unauthorized), which is caught by the frontend.
    """
    return {"message": "Token is valid", "user": current_user}
