from fastapi import Depends, FastAPI

from app.auth.dependencies import get_current_user
from app.database import Base, engine
from app.models import User, LearningSession, Evaluation
from app.routers import auth, sessions, evaluations


# Create database tables

# Create FastAPI application
app = FastAPI(
    title="Bodhrik Education Platform API",
    version="1.0.0",
)


# Register routers
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(evaluations.router)


@app.get("/")
def root():
    return {
        "message": "Bodhrik Education Platform API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }