
from uuid import uuid4

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def get_auth_headers():
    username = f"testuser_{uuid4().hex[:8]}"
    password = "TestPassword123"

    client.post(
        "/register",
        json={"username": username, "password": password}
    )

    response = client.post(
        "/login",
        data={"username": username, "password": password}
    )

    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_get_products():
    headers = get_auth_headers()
    response = client.get("/products", headers=headers)
    assert response.status_code == 200


def test_create_product():
    headers = get_auth_headers()

    response = client.post(
        "/products",
        json={
            "name": "Test Mouse",
            "price": 500,
            "quantity": 10,
            "category": "Electronics"
        },
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Test Mouse"


def test_product_not_found():
    headers = get_auth_headers()
    response = client.get("/products/999999", headers=headers)
    assert response.status_code == 404
