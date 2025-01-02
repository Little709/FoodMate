from sys import prefix
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router  # Absolute import
from chat.routes import router as chat_router  # Includes chat-related routes
from management.routes import router as account_router
from recipes.routes import router as recipes_router
from utils.database import Base, general_engine as engine, notification_manager  # Absolute import
from utils.authutils import get_current_user
import logging
import os
# from backend.utils.database import Base, notification_manager

# Set up logging
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.DEBUG)  # You can adjust the level to DEBUG for more verbosity

API_IP = os.getenv("API_IP", "127.0.0.1")
API_PORT = os.getenv("API_PORT", 8000)

def create_app() -> FastAPI:
    app = FastAPI(title="FoodMate", lifespan=lifespan)

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

# Lifespan handler to start notification listening
async def lifespan(app: FastAPI):
    logger.info("Registered lifespan app")
    # Startup operations
    try:
        await notification_manager.connect()  # Establish connection to the database
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise e  # Exit the app startup if connection fails

    # Pass control to the app
    yield

    # Shutdown operations
    if notification_manager.connection:
        try:
            await notification_manager.connection.close()
            logger.info("Database connection closed successfully.")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")



app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=API_IP, port=int(API_PORT), reload=True)
