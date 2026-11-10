# Inventory Management API

A backend application built using Python and FastAPI to manage inventory products with secure user authentication and PostgreSQL database integration.

## Features

- User registration and login
- Password hashing for secure password storage
- JWT-based authentication
- Create new products
- View all products
- View individual products
- Update product details
- Delete products
- PostgreSQL database integration
- Automated API testing using pytest

## Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT, OAuth2
- **Password Security:** pwdlib
- **Testing:** pytest, FastAPI TestClient
- **API Documentation:** Swagger UI
- **Environment Management:** python-dotenv

## Project Structure

```text
inventory_management_api/
│
├── main.py
├── database.py
├── test_main.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

## Setup Instructions

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your secret key:

```env
SECRET_KEY=your_secret_key
```

5. Configure your PostgreSQL database connection in `database.py`.

6. Start the application:

```bash
uvicorn main:app --reload
```

## API Documentation

Once the application is running, open:

`http://127.0.0.1:8000/docs`

Swagger UI provides interactive API documentation and testing.

## Run Automated Tests

```bash
python -m pytest -v
```

## Authentication

Product endpoints require a valid JWT access token. Users must register and log in to access protected inventory operations.

## Project Status

Core CRUD operations, database integration, JWT authentication, and automated tests implemented.