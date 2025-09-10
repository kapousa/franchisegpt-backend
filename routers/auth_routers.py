from fastapi import APIRouter, HTTPException
from src.schemas.User import User
from src.utils.DB_Utils import hash_password, verify_password
from src.services.auth_service import AuthService
from src.services.db_service import DBService

router = APIRouter(prefix="/auth", tags=["auth"])
db = DBService()

@router.post("/signup")
def signup(user: User):
    hashed = hash_password(user.password)
    db.save_user(user.username, hashed)
    return {"message": "User registered"}

@router.post("/login")
def login(user: User):
    db_user = db.get_user(user.username)
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = AuthService.create_token(user.username)
    return {"access_token": token}
