import os
from jose import jwt
from jose.exceptions import JWTError as PyJWTError

from starlette.authentication import AuthCredentials, SimpleUser, BaseUser, AuthenticationBackend
from starlette.requests import Request
from starlette.exceptions import HTTPException
from sqlalchemy.orm import Session

from dotenv import load_dotenv

from config import get_sqlite_db_sync, SessionLocal
from src.models.User import User as SQLUser

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

class AuthenticatedUser(BaseUser):
    """Custom user class to hold our SQLAlchemy User object"""
    def __init__(self, user: SQLUser):
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.user.email

    @property
    def identity(self) -> str:
        return str(self.user.id)

class AnonymousUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return "Anonymous"

    @property
    def identity(self) -> str:
        return "anonymous"


class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: Request):
        print(f"\n--- DEBUG: JWTAuthBackend.authenticate called for path: {conn.url.path} ---")

        if "Authorization" not in conn.headers:
            print("DEBUG: No Authorization header found.")
            return None

        auth_header = conn.headers["Authorization"]
        if not auth_header.startswith("Bearer "):
            print("DEBUG: Authorization header is not a Bearer token.")
            return None

        token = auth_header.split(" ")[1]
        print(f"DEBUG: Token extracted: {token[:30]}... (first 30 chars)")

        db: Session = SessionLocal()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_from_token: str = payload.get("sub")

            print(f"DEBUG: JWT Payload: {payload}")
            print(f"DEBUG: User ID ('sub' claim) from token: {user_id_from_token}")

            if user_id_from_token is None:
                print("DEBUG: User ID ('sub' claim) is missing in token payload.")
                return None

            user_id_for_query = user_id_from_token

            user = db.query(SQLUser).filter(SQLUser.id == user_id_for_query).first()

            if user is None:
                print(f"DEBUG: User not found in DB for ID: {user_id_for_query}")
                return None

            print(f"DEBUG: User found in DB: {user.email} (ID: {user.id})")
            print("DEBUG: Authentication successful.")
            return AuthCredentials(["authenticated"]), AuthenticatedUser(user)

        except PyJWTError as e: # This now correctly catches jose.exceptions.JWTError aliased as PyJWTError
            print(f"DEBUG: PyJWTError (Invalid Token): {e}")
            return None
        except Exception as e:
            print(f"DEBUG: UNEXPECTED ERROR during authentication: {e}", exc_info=True)
            return None
        finally:
            if db:
                db.close()