from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("api_logger")

class UserProfileIncompleteError(Exception):

    def __init__(self, missing_fields: list):
        self.missing_fields = missing_fields
    
def setup_exception_handlers(app: FastAPI):

    @app.exception_handler(UserProfileIncompleteError)
    async def profile_incomplete_handler(request: Request, exc: UserProfileIncompleteError):
        logger.warning(f"Profile incomplete. Missing: {exc.missing_fields}")
        return JSONResponse(
            status_code = 422,
            content={
            "error": "Profile incomplete", 
            "missing_fields": exc.missing_fields,
            "message": "Please provide the missing fields to continue."
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server error at {request.url.path}: {str(exc)}", exc_info= True)
        return JSONResponse(
                status_code=500,
                content={"error": "An unexpected server error occurred.Please try again later."}
        )