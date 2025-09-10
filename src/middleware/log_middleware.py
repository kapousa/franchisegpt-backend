# middleware/log_middleware.py

import time
import json
from datetime import datetime  # Make sure datetime is imported here
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp
import traceback as tb_module  # Import for getting traceback string
from starlette.authentication import (
    AuthenticationBackend, AuthCredentials, SimpleUser
)
from src.models.APILog import APILog  # Ensure this import is correct
from src.utils import Helper
from src.utils.Logger import logger  # Ensure this import is correct
from config import SessionLocal  # Import SessionLocal for direct use


class LogRequestsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 1. Start a new DB session for this middleware
        db = SessionLocal()
        log_record = None  # Initialize to None
        log_record_to_update = None  # Initialize to None
        start_time = time.time()
        user_id_for_initial_log = None

        try:
            # Attempt to get user_id even if not authenticated
            # if hasattr(request, "user") and request.user.is_authenticated:
            #     user_id_for_initial_log = str(request.user.identity)
            # else:
            #     user_id_for_initial_log = None  # Or 'guest' or some other indicator

            # Initial log record creation with NEW MODEL FIELDS
            log_record = APILog(
                id=Helper.generate_id(),
                timestamp=datetime.utcnow(),  # Use utcnow for consistency with model default
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params) if request.query_params else None,  # Ensure it's string or None
                # Removed 'request_body' and 'response_body' as they are not in your APILog model
                status_code=500,  # Default to 500 in case of crash before response
                status_description="Pending",  # New field for initial status
                duration="0.0",  # New field, storing as string as per your model's 'duration'
                user_id=user_id_for_initial_log,
                error_message=None,  # Initialize as None
                traceback=None  # Initialize as None
            )
            db.add(log_record)
            db.commit()  # Commit the initial log to get an ID
            db.refresh(log_record)  # Refresh to get the generated ID and keep it 'fresh'

            # Store the log record ID in request.state for later updates
            request.state.log_record_id = log_record.id
            log_record_to_update = log_record  # Assign to the variable used in the finally block

            # Process the request
            response = await call_next(request)

            # Update log record with response details
            if log_record_to_update:
                db.refresh(log_record_to_update)  # Re-bind/refresh before updating
                log_record_to_update.status_code = response.status_code
                log_record_to_update.duration = f"{(time.time() - start_time):.4f}s"  # Format as string

                # Set status_description based on status_code
                if 200 <= response.status_code < 300:
                    log_record_to_update.status_description = "Success"
                elif 400 <= response.status_code < 500:
                    log_record_to_update.status_description = "Client Error"
                else:
                    log_record_to_update.status_description = "Server Error"

                # Do not try to log request_body or response_body as they are not in your model

                db.add(log_record_to_update)  # Re-add to session if it somehow became detached
                db.commit()
                # db.refresh(log_record_to_update) # Not strictly needed after final commit unless you use it later

        except Exception as e:
            # Handle exceptions that occur *within* the middleware or downstream
            logger.error(f"Error in LogRequestsMiddleware: {e}", exc_info=True)

            # If an initial log record was created, try to update it with error info
            if log_record_to_update:
                try:
                    db.refresh(log_record_to_update)  # Re-bind/refresh before updating
                    log_record_to_update.status_code = 500  # Set to 500 for unhandled errors
                    log_record_to_update.duration = f"{(time.time() - start_time):.4f}s"
                    log_record_to_update.status_description = "Unhandled Exception"
                    log_record_to_update.error_message = str(e)[:500]  # Truncate error message for DB
                    log_record_to_update.traceback = tb_module.format_exc()  # Get full traceback string
                    db.add(log_record_to_update)
                    db.commit()
                except Exception as update_e:
                    logger.error(f"Failed to update APILog record after error: {update_e}")

            # Re-raise the exception so FastAPI's global exception handlers can catch it
            raise e
        finally:
            # Always close the database session to release the connection
            if db:
                db.close()

        # Ensure a response is always returned.
        # If an exception was raised, FastAPI's exception handler will return a response.
        # If no exception, 'response' is from call_next.
        return response