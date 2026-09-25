
# This file creates the main FastAPI application
# for the College Service Request System.

from fastapi import FastAPI

from app.config import settings
from app.database import ping_database
from app.routers import users
from app.routers import categories

# Create the FastAPI app instance
app = FastAPI(title=settings.APP_NAME)

# Register the users router
app.include_router(users.router)
app.include_router(categories.router)


# Check the database connection when the server starts
@app.on_event("startup")
def on_startup() -> None:
    if not ping_database():
        raise RuntimeError("Could not connect to MongoDB")

    print(f"[startup] Connected to MongoDB. App: {settings.APP_NAME}")


# Basic health-check endpoint
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME
    }