# com/routers/users_router.py

import uuid
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from config import get_sqlite_db_sync
from src.services.auth.jwt_security import create_access_token, verify_password, get_password_hash, get_current_user
from src.models.User import User as SQLUser
from src.schemas.User import User, UserCreate, Token

router = APIRouter(prefix="/users", tags=["users"])

@router.get(("/"))
def user_index():
    return {"message": "Welcome user"}

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_sqlite_db_sync)):
    hashed_password = get_password_hash(user.password)
    # Ensure ID is generated as a UUID string, consistent with your model
    db_user = SQLUser(id=str(uuid.uuid4()), username=user.username, email=user.email, password=hashed_password, avatar="", role="patient")
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already registered")

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_sqlite_db_sync)):
    # Load user with roles eager-loaded for efficiency
    user = db.query(SQLUser).options(joinedload(SQLUser.roles)).filter(SQLUser.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_role_names = [role.name for role in user.roles]

    # --- CRITICAL FIX: Set 'sub' claim to the user's actual ID (UUID string) ---
    access_token_data = {
        "sub": str(user.id),  # Use the user's UUID ID as a string
        "roles": user_role_names,
        "email": user.username
    }
    access_token = create_access_token(data=access_token_data)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    # The current_user is already populated by get_current_user (which uses JWTAuthBackend)
    return current_user

@router.get("/all", response_model=List[User])
async def read_users(db: Session = Depends(get_sqlite_db_sync)):
    users = db.query(SQLUser).all()
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: str, db: Session = Depends(get_sqlite_db_sync)):
    # User ID is a string (UUID) here
    db_user = db.query(SQLUser).filter(SQLUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user