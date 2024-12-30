from sys import prefix
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router  # Absolute import
from chat.routes import router as chat_router  # Includes chat-related routes
from management.routes import router as account_router
from recipes.routes import router as recipes_router
from utils.database import Base, engine  # Absolute import
from utils.authutils import get_current_user
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # You can adjust the level to DEBUG for more verbosity

API_IP = os.getenv("API_IP", "127.0.0.1")
API_PORT = os.getenv("API_PORT", 8000)

def create_app() -> FastAPI:
    app = FastAPI(title="FoodMate")

    # Enable CORS (update the allowed origins in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update for frontend origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create DB tables
    Base.metadata.create_all(bind=engine)

    # Public routes (register and login)
    app.include_router(auth_router, prefix="/auth", tags=["auth"])

    # Protected routes (require authentication)
    app.include_router(
        account_router,
        prefix="/management",
        tags=["management"],
        dependencies=[Depends(get_current_user)],
    )

    # Chat routes (no user validation for now, can be updated)
    app.include_router(
        chat_router,
        prefix="/chat",
        tags=["chat"]
    )

    # Recipes routes (requires authentication)
    app.include_router(
        recipes_router,
        prefix="/recipes",
        tags=["recipes"],
        dependencies=[Depends(get_current_user)],
    )

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=API_IP, port=int(API_PORT), reload=True)
