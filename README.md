# Inventory Management System

A full-stack inventory application built with React, FastAPI, PostgreSQL, JWT authentication, Docker and pytest.

## Features
- User registration and JWT login
- Authenticated product CRUD
- Search by product name/category and category filter
- Inventory metrics and low-stock indicator
- Docker Compose PostgreSQL + API setup

## Run with Docker
1. Install Docker Desktop.
2. From the project root run:
   ```bash
   docker compose up --build
   ```
3. API docs: http://localhost:8002/docs
4. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. Open http://localhost:5173

## Register a user
Use `POST /register` in Swagger with:
```json
{"username":"your_username","password":"choose_a_password_8_chars_or_more"}
```
Then sign in from the frontend.

## Local backend without Docker
Set `DATABASE_URL` to a reachable PostgreSQL database, install `backend/requirements.txt`, then run:
```bash
cd backend
uvicorn main:app --reload --port 8002
```

## Tests
From `backend`:
```bash
pytest -q
```

## Environment and security
- Copy `backend/.env.example` to `backend/.env` for local configuration if needed.
- Never commit `.env`, passwords, database credentials, or production JWT secrets.
- The default Compose credentials and JWT secret are for local development only. Change them before deployment.
- Configure `VITE_API_URL` at frontend build time when deploying the frontend.
