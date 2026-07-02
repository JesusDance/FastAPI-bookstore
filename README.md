# FastAPI-bookstore

## Description:
A RESTfull API for managing a bookstore where users can get books from https://openlibrary.org/
and collect this books in database.

## Features:
- FastAPI RESTfull CRUD operations
- Pydentic models for validation
- SQLAlchemy ORM
- PostgreSQL as the main database
- Alembic migrations
- Authentication with password hashing (pwdlib -> Argon2)
- Async Httpx client in lifecycle with DI
- Basic Auth for main page
- JWT authorization
- Async Unit tests with Pytest using SQLite
- Dockerfile with docker-compose
- Redis for caching queries
- Rate limit by ip using redis
- Logging for client
- Deploy using Render
- Neon database for cloud host

# Installation

## 1. Clone repo
1. git clone https://github.com/JesusDance/FastAPI-bookstore
2. cd FastAPI-bookstore

## 2. Create virtual environment
1. python -m venv .venv
2. source .venv/bin/activate  # Linux/Mac
3. .venv\Scripts\activate     # Windows

## 3. Install dependencies
pip install -r requirements.txt

## 4. Run app
1. docker build -t bookstore-api .
2. docker-compose up -d
3. uvicorn app.main:app --reload

## App runs at:
- http://127.0.0.1:8000
- http://localhost:8080
- http://127.0.0.1:3000

## Swagger:
- http://127.0.0.1:8000/docs
- http://localhost:8080/docs
- http://127.0.0.1:3000/docs

## Routes:
- '/': main endpoint (username: admin, password: admin_pass)
- '/register': user registration
- '/register/login': user authentication (JWT token)
- '/bookstore': protected routes for managing books
- https://fastapi-bookstore-a0pj.onrender.com
- https://fastapi-bookstore-a0pj.onrender.com/docs OpenAPI swagger
