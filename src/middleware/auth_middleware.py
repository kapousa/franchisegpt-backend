from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from src.services.auth_service import AuthService

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
            user = AuthService.decode_token(token)
            if user:
                request.state.user = user
        response = await call_next(request)
        return response
