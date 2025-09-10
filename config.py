# src/config.py

import logging
import os
import sqlite3
import threading # Added for debugging thread IDs
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# For MongoDB (SYNCHRONOUS) - using pymongo
from pymongo import MongoClient
from pymongo.database import Database  # For type hinting
from pymongo.server_api import ServerApi # For recommended Server API version

# Load environment variables
load_dotenv()

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- SQLite Configuration (SYNCHRONOUS SQLAlchemy - Unchanged) ---
DATABASE_FILE = "tahlyl-local-dbe.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Synchronous SQLAlchemy Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_connection():
    """Gets a new raw synchronous connection to the SQLite database. (Less common with SQLAlchemy)"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        logger.info(f"Thread {threading.get_ident()}: Raw SQLite connection established.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Thread {threading.get_ident()}: Error connecting to raw SQLite database: {e}")
        raise


def get_sqlite_db_sync():
    """
    FastAPI Dependency: Provides a synchronous SQLAlchemy session for SQLite.
    This session will be run in a threadpool when called from an async endpoint.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.info(f"Thread {threading.get_ident()}: Synchronous SQLAlchemy session closed.")


def create_sqlite_tables_sync():
    """Creates all defined SQLite tables synchronously."""
    Base.metadata.create_all(bind=engine)
    logger.info("Synchronous SQLite tables creation attempt complete.")


# --- MongoDB Configuration (SYNCHRONOUS) ---
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
# Initialize mongo_client and mongo_database as None globally
# They will be set by connect_to_mongo() for each worker process
_mongo_client: Optional[MongoClient] = None # Use underscore to prevent name clash if needed
_mongo_database: Optional[Database] = None


# --- UPDATED: Connect/Close functions run per worker process ---
def connect_to_mongo():
    """Establishes connection to MongoDB synchronously for a single worker process."""
    global _mongo_client, _mongo_database
    logger.info(f"Thread {threading.get_ident()}: Attempting to connect to MongoDB.")
    try:
        if not MONGO_DETAILS:
            logger.error("MONGO_DETAILS environment variable is not set. Please set it in your .env file.")
            raise ValueError("MongoDB connection string (MONGO_DETAILS) is missing.")

        _mongo_client = MongoClient(MONGO_DETAILS, server_api=ServerApi('1')) # Use ServerApi for Atlas
        _mongo_database = _mongo_client.get_database("tahlyl") # Replace with your actual MongoDB database name

        # Optional: Ping the admin database to confirm a successful connection
        # _mongo_client.admin.command('ping')
        logger.info(f"Thread {threading.get_ident()}: MongoDB Atlas connection successful!")
    except Exception as e:
        logger.error(f"Thread {threading.get_ident()}: Could not connect to MongoDB: {e}")
        _mongo_client = None
        _mongo_database = None
        raise # Re-raise to signal startup failure


def close_mongo_connection():
    """Closes the MongoDB connection synchronously for a single worker process."""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None # Clear reference
        logger.info(f"Thread {threading.get_ident()}: MongoDB connection closed.")


def get_mongo_db_sync(): # Renamed for clarity: _sync
    """FastAPI Dependency: Provides the synchronous MongoDB database object."""
    # Check if _mongo_database has been initialized in THIS worker process
    if _mongo_database is None:
        logger.error(f"Thread {threading.get_ident()}: Attempted to get MongoDB database before connection was established in this process.")
        raise RuntimeError("MongoDB database not initialized for this worker process. Check startup events.")
    return _mongo_database