# Bodhrik Education Platform API

A backend service for an education platform built as part of the Bodhrik AI Fellow Full Stack Development Technical Assessment.

The application provides APIs for managing users, teachers, parents, students, learning sessions, and evaluations. It demonstrates authentication, role-based access control, PostgreSQL data modeling, Redis-based asynchronous processing, Dockerized deployment, database migrations, automated testing, and continuous integration.


# 1. Assessment Requirements

This repository contains the complete technical assessment implementation, including:

- FastAPI backend service
- PostgreSQL database
- Users, Sessions, and Evaluations data models
- CRUD APIs for learning sessions
- JWT authentication
- Role-based access control
- Teacher resource-level authorization
- Parent-child authorization
- Redis-based evaluation queue
- Docker Compose setup
- Alembic database migrations
- Automated tests
- Ruff linting
- GitHub Actions CI
- Database and architecture documentation
- Complete Git commit history

The repository contains the complete development history through incremental Git commits.


# 2. Technology Stack

- FastAPI
- Python 3.12
- PostgreSQL 16
- SQLAlchemy
- JWT
- bcrypt
- Redis 7
- Alembic
- Pytest
- Ruff
- Docker
- Docker Compose
- GitHub Actions
- Swagger / OpenAPI

# 3. Application Architecture

The application follows a backend service architecture with FastAPI as the main API layer.

# Main Components

1. **Client**
   - Sends HTTP requests to the FastAPI application.
   - Swagger UI can be used as an interactive client.

2. **FastAPI**
   - Handles API requests.
   - Handles authentication and JWT validation.
   - Applies role-based access control.
   - Provides session CRUD APIs.
   - Provides the evaluation endpoint.

3. **PostgreSQL**
   - Stores users.
   - Stores learning sessions.
   - Stores evaluations.
   - Maintains relationships between users, parents, students, teachers, and sessions.

4. **Redis**
   - Acts as an asynchronous evaluation queue.
   - Stores evaluation jobs waiting to be processed.

5. **Alembic**
   - Manages database schema migrations.
   - Keeps database changes version controlled.

6. **Docker Compose**
   - Runs the FastAPI application, PostgreSQL, and Redis as separate services.

### Evaluation Request Flow

1. Client sends an evaluation request.
2. FastAPI authenticates the user.
3. FastAPI checks the user's authorization.
4. An evaluation record is created in PostgreSQL.
5. The evaluation job is added to the Redis queue.
6. The API returns HTTP `202 Accepted`.
7. A background worker can process the queued evaluation asynchronously.
  v
HTTP 202 Accepted
