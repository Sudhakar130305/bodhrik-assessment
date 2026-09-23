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

FastAPI
Python 3.12 
PostgreSQL 16 
SQLAlchemy
JWT
bcrypt
Redis 7
Alembic
Pytest
Ruff
Docker 
Swagger.


# 3. Application Architecture

Client
  |
  v
POST /sessions/{session_id}/evaluate
  |
  v
Authentication
  |
  v
Authorization
  |
  v
Create Evaluation
  |
  v
Redis Queue
  |
  v
HTTP 202 Accepted
