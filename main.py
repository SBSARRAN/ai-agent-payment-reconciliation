
# IMPORTS


# FastAPI is the backend API framework.
from fastapi import FastAPI

# Import the routes we will create in routes.py.
from backend.api.routes import router



# CREATE FASTAPI APP


# This creates our FastAPI application.
app = FastAPI(
    title="AI Payment Reconciliation API",
    version="1.0.0"
)



# ADD API ROUTES


# Include all endpoints from routes.py.
app.include_router(router)



# TEST HOME ROUTE


# GET /
# Use:
# Simple test to check whether FastAPI is running.
@app.get("/")
def home():

    return {
        "message": "AI Payment Reconciliation API is running"
    }