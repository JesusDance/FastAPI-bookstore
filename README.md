# FastAPI-bookstore

## Description:
A RESTfull API for managing a bookstore where users(authors) can create books
and bookstore for collecting this books.

## Features:
- FastAPI RESTfull CRUD operations
- Pydentic models for validation
- SQLAlchemy ORM
- PostgreSQL as the main database
- Alembic migrations
- Authentication with password hashing (pwdlib -> Argon2)
- JWT authorization
- Pytest using SQLite
- Dockerfile with docker-compose
- Deploy using Render
- Neon database for cloud host

## Routes:
- '/': main endpoint
- '/register': user registration
- '/register/login': user authentication (JWT token)
- '/bookstore': protected routes for managing books
- https://fastapi-bookstore-a0pj.onrender.com
- https://fastapi-bookstore-a0pj.onrender.com/docs OpenAPI swagger
