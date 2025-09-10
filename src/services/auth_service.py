from datetime import datetime, timedelta
import jwt

SECRET_KEY = "supersecret"  # move to .env in production
ALGORITHM = "HS256"

class AuthService:
    @staticmethod
    def create_token(user_id: str):
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
