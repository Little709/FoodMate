from sys import prefix

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router  # Absolute import
from chat.routes import router as chat_router
from management.routes import router as account_router
from recipes.routes import router as recipes_router
from utils.database import Base, engine  # Absolute import
from utils.authutils import get_current_user

import os

API_IP = os.getenv("API_IP")
API_PORT = os.getenv("API_PORT")

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
    app.include_router(auth_router,prefix="/auth", tags=["auth"])


    # Protected routes (require authentication)
    app.include_router(account_router, prefix="/management", tags=["management"], dependencies=[Depends(get_current_user)])

    # Custom dependency for /chat routes
    def validate_user(current_user=Depends(get_current_user)):
        if not current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
        return current_user
    # app.include_router(chat_router,prefix="/chat", tags=["chat"], dependencies=[Depends(validate_user)]) #TODO: no dependance on get_current_user. meaning unsafe?
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    app.include_router(recipes_router,prefix="/recipes", tags=["recipes"], dependencies=[Depends(get_current_user)])

    return app


app = create_app()
for route in app.routes:
    print(route)

if __name__ == "__main__":
    uvicorn.run(app, host=API_IP, port=int(API_PORT), reload=True)
