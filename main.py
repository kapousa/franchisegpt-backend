from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from config import create_sqlite_tables_sync, connect_to_mongo, close_mongo_connection
from middleware.log_middleware import LogRequestsMiddleware
from src.middleware.auth_middleware import AuthMiddleware
from routers import (
    rag_routers, auth_routers, agent_routers, data_routers, users_router
)
from src.services.auth.auth_backend import JWTAuthBackend
from src.utils.Logger import logger

app = FastAPI(title="FranchiseGPT Backend")

# ✅ Add authentication middleware
# --- Middleware Registration Order ---
app.add_middleware(LogRequestsMiddleware)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())
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
app.include_router(users_router)

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

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI application startup event triggered.")
    create_sqlite_tables_sync() # Ensure SQLite tables are created (can be here or at global scope)
    connect_to_mongo() # Establish MongoDB connection for this worker process

@app.on_event("shutdown")
def shutdown_event():
    logger.info("FastAPI application shutdown event triggered.")
    close_mongo_connection()

@app.get("/")
def root():
    return {"message": "FranchiseGPT Backend is running 🚀"}
