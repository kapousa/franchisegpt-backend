from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.middleware.auth_middleware import AuthMiddleware
from routers import (
    rag_routers, auth_routers, agent_routers, data_routers
)
from src.utils.Logger import logger

app = FastAPI(title="FranchiseGPT Backend")

# ✅ Add authentication middleware
# --- Middleware Registration Order ---
#app.add_middleware(LogRequestsMiddleware)
#app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"], # Consider narrowing this down for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(rag_routers)
app.include_router(auth_routers)
app.include_router(agent_routers)
app.include_router(data_routers)

# --- Global Exception Handlers ---
@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception for request: {request.method} {request.url}",
        exc_info=True,
        extra={
            "request_id": getattr(request.state, "request_id", "N/A"),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected server error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", "N/A"),
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} for request: {request.method} {request.url}",
        extra={
            "request_id": getattr(request.state, "request_id", "N/A"),
            "status_code": exc.status_code,
            "detail": exc.detail,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "request_id": getattr(request.state, "request_id", "N/A")},
    )


@app.get("/")
def root():
    return {"message": "FranchiseGPT Backend is running 🚀"}
