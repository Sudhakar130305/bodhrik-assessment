# Bodhrik Education Platform API

FastAPI-based backend service for managing users, learning sessions, and evaluations.

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- JWT Authentication
- Docker Compose
- Pytest
- GitHub Actions

## Running the Project

Create a `.env` file containing:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/bodhrik
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change-this-secret