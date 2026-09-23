# Bodhrik Education Platform API

A backend service for an education platform.

The application provides APIs for managing users, teachers, parents, students, learning sessions, and evaluations. It demonstrates authentication, role-based access control, PostgreSQL data modeling, Redis-based asynchronous processing, Dockerized deployment, database migrations, automated testing, and continuous integration.


# 1. Features

- User registration and JWT-based authentication
- Role-based access control
- Learning Session CRUD operations
- Evaluation creation and queueing
- Redis-based evaluation queue
- SQLAlchemy ORM
- Alembic database migrations
- Dockerized application
- Automated tests using Pytest
- Swagger API documentation
- Health check endpoint

# 2. Technology Stack

- FastAPI
- Python 3.12
- PostgreSQL 16
- SQLAlchemy
- JWT
- Redis 7
- Alembic
- Pytest
- Docker
- Swagger

# 3. System Design & Evaluation Flow

The application follows a backend service architecture with FastAPI as the main API layer.

### Main Components

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
   - Stores users, learning sessions, and evaluations.
   - Maintains relationships between parents, students, teachers, and sessions.

4. **Redis**
   - Acts as an asynchronous evaluation queue.
   - Stores evaluation jobs waiting to be processed.

5. **Alembic**
   - Manages database schema migrations.
   - Keeps database changes version controlled.

6. **Docker Compose**
   - Runs FastAPI, PostgreSQL, and Redis as separate services.

The application follows a backend service architecture with FastAPI as the main API layer.

1. Client sends an evaluation request.
2. FastAPI authenticates the user.
3. FastAPI checks the user's authorization.
4. An evaluation record is created in PostgreSQL.
5. The evaluation job is added to the Redis queue.
6. The API returns HTTP `202 Accepted`.

## 4. Requirements

Before running the project, make sure the following are installed:

- Git
- Docker Desktop
- Docker Compose

No local PostgreSQL or Redis installation is required because both services run inside Docker containers.

Verify the installations:

```bash
git --version
docker --version
docker compose version
```

---

## 5. Installation

Clone the repository:

```bash
git clone https://github.com/Sudhakar130305/bodhrik-assessment.git
cd bodhrik-assessment
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/bodhrik
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secure-secret-key
```

The `.env` file contains environment-specific configuration and is excluded from Git using `.gitignore`.

A `.env.example` file can be used as a template for other developers.

---

## 6. Running the Application

Build and start the application:

```bash
docker compose up -d --build
```

Check the running containers:

```bash
docker compose ps
```

The application runs the following services:

- FastAPI API
- PostgreSQL database
- Redis queue

The API is available at:

```text
http://localhost:8001
```

Stop the application:

```bash
docker compose down
```

To stop the application and remove the database volume:

```bash
docker compose down -v
```

---

## 7. API Documentation

FastAPI provides interactive API documentation using Swagger UI.

### Swagger UI

```text
http://localhost:8001/docs
```

Swagger can be used to test authentication, session CRUD operations, RBAC, and evaluation endpoints.

### ReDoc

```text
http://localhost:8001/redoc
```

### Health Check

```http
GET /health
```

Open:

```text
http://localhost:8001/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## 8. Database Migrations

Alembic is used to manage database schema migrations.

Apply the latest migration:

```bash
docker exec -it bodhrik_api alembic upgrade head
```

Check the current migration:

```bash
docker exec -it bodhrik_api alembic current
```

View migration history:

```bash
docker exec -it bodhrik_api alembic history
```

Database tables are managed through Alembic migrations instead of being automatically created when the application starts.

---

## 9. Authentication

The API uses JWT-based authentication.

### Register User

```http
POST /auth/register
```

Example request:

```json
{
  "name": "Teacher One",
  "email": "teacher@example.com",
  "password": "password123",
  "role": "teacher"
}
```

Supported roles:

```text
admin
teacher
parent
student
```

### Login

```http
POST /auth/login
```

Example request:

```json
{
  "email": "teacher@example.com",
  "password": "password123"
}
```

The login endpoint returns a JWT access token.

The token can be provided in Swagger using the `Authorize` button:

```text
Bearer <your-token>
```

Passwords are hashed using bcrypt and are never stored as plain text.

---

## 10. Role-Based Access Control

The application implements server-side role-based access control.

### Admin

Admins can access all sessions and perform administrative operations.

### Teacher

Teachers can:

- Create sessions assigned to themselves
- View their own sessions
- Update their own sessions
- Delete their own sessions
- Trigger evaluations for their own sessions

A teacher cannot access another teacher's sessions.

### Parent

Parents can only access sessions belonging to their own children.

A parent cannot access another parent's child's sessions.

### Student

Students represent child accounts in the platform and can be associated with a parent account.

Authorization is enforced by the backend rather than relying only on frontend restrictions.

---

## 11. Session Management

The API provides CRUD operations for learning sessions.

### Create Session

```http
POST /sessions
```

Example request:

```json
{
  "title": "Mathematics Session",
  "teacher_id": 2,
  "child_id": 3,
  "scheduled_at": "2026-09-20T10:00:00"
}
```

### List Sessions

```http
GET /sessions
```

The sessions returned depend on the authenticated user's role.

### Get Session

```http
GET /sessions/{session_id}
```

### Update Session

```http
PUT /sessions/{session_id}
```

### Delete Session

```http
DELETE /sessions/{session_id}
```

Protected session operations validate authentication, user roles, and resource ownership before allowing access.

---

## 12. Evaluation Trigger

The application provides an evaluation trigger for learning sessions.

Endpoint:

```http
POST /sessions/{session_id}/evaluate
```

When an authorized teacher or admin triggers an evaluation, the following flow is used:

```text
Client
  ↓
POST /sessions/{session_id}/evaluate
  ↓
Authentication
  ↓
Authorization
  ↓
Create Evaluation
  ↓
Redis Evaluation Queue
  ↓
HTTP 202 Accepted
```

The evaluation is initially stored with:

```text
status = queued
```

The API then places an evaluation job into Redis.

Example queue payload:

```json
{
  "evaluation_id": 1,
  "session_id": 10
}
```

The endpoint returns HTTP `202 Accepted` because the evaluation is queued for asynchronous processing instead of being processed synchronously during the API request.

---

## 13. Redis Usage

Redis is used as an asynchronous evaluation queue.

Queue name:

```text
evaluation_queue
```

Evaluation jobs are pushed into the Redis list when the evaluation endpoint is triggered.

Check the number of queued jobs:

```bash
docker exec -it bodhrik_redis redis-cli LLEN evaluation_queue
```

Inspect queued jobs:

```bash
docker exec -it bodhrik_redis redis-cli LRANGE evaluation_queue 0 -1
```

This provides meaningful use of Redis as a queue for asynchronous evaluation processing.

In a production environment, a dedicated worker can consume jobs from this queue, process evaluations, update the database, and implement retry and failure handling.

---

## 14. Testing

The project uses Pytest for automated API and RBAC testing.

Run the complete test suite:

```bash
docker exec -it bodhrik_api pytest -v
```

The test suite covers:

- Health endpoint
- User registration and login
- Teacher session isolation
- Parent child-session isolation
- Unauthenticated session access
- Evaluation queue creation

Expected result:

```text
6 passed
```

The tests verify both application functionality and authorization boundaries.

---

## 16. Project Structure

```text
bodhrik-assessment/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── routers/
│       ├── auth.py
│       ├── sessions.py
│       └── evaluations.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── tests/
│   └── test_api.py
│
├── screenshots/
│   ├── docker.png
│   ├── swagger.png
│   ├── authentication.png
│   ├── session-crud.png
│   ├── teacher-rbac.png
│   ├── parent-rbac.png
│   ├── redis-queue.png
│   ├── postgres.png
│   ├── tests.png
│   └── github-actions.png
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── DESIGN.md
└── README.md
```


<img width="680" height="842" alt="Screenshot 2026-09-23 190406" src="https://github.com/user-attachments/assets/5790b68d-11f6-4109-ac1d-1377f041ca2f" />
