import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:12345@localhost/test_personal_db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def clear_db():
    """Ma'lumotlar bazasini yaratish va tozalash fixture"""
    Base.metadata.create_all(bind=engine)  # Testlar oldidan DB yaratish
    yield
    Base.metadata.drop_all(bind=engine)  # Testlardan keyin DB ni tozalash


def override_get_db():
    """Testlar davomida foydalaniladigan DB session yaratish"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)
def test_signup_success():
    user1 = {
        "username": "Davronbek3333ddd",
        "email": "davronbekatadjando3dd33@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user1)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["success"] == True
    assert response_data["status"] == 201
    assert response_data["message"] == "User is created successfully"

    data = response_data["data"]
    assert data["username"] == "Davronbek3333ddd"
    assert data["email"] == "davronbekatadjando3dd33@gmail.com"
    assert data["is_active"] == True

    user_setting = data["user_setting"]
    assert user_setting["currency"] == "UZS"  # Default qiymat
    assert user_setting["reminder_time"] == 1  # Default qiymat


def test_signup_dublicat_email():
    # foydanauvchi 1
    user1 = {
        "username": "Davronbek1",
        "email": "davronbek1@gamil.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user1)
    assert response.status_code == 201

    # foydanuvchi 2
    user2 = {
        "username": "Davronbek2",
        "email": "davronbek1@gamil.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user2)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "User with this email already exists"
    }

def test_signup_dublicat_username():
    # foydalanuvchi 1
    user1 = {
        "username": "Davronbek1",
        "email": "davronbek1@gamil.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user1)
    assert response.status_code == 201

    # foydalanuvchi 2
    user2 = {
        "username": "Davronbek1",
        "email": "davronbek2@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user2)

    assert response.status_code == 400

    assert response.json() == {
        "detail": "User with this username already exists"
    }

def test_signup_optional_fields():
    user = {
        "username": "Davronbek1",
        "email": "davronbek2@gmail.com",
        "password": "Davronbek",
    }
    response = client.post('/auth/signup', json=user)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["success"] == True
    assert response_data["status"] == 201
    assert response_data["message"] == "User is created successfully"

    data = response_data["data"]
    assert data["username"] == "Davronbek1"
    assert data["email"] == "davronbek2@gmail.com"
    assert data["is_active"] == False  # Default qiymat shunday

    user_setting = data["user_setting"]
    assert user_setting["currency"] == "UZS"
    assert user_setting["reminder_time"] == 1


def test_login_username_success():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "password",
        "is_active": True
    }
    response = client.post("/auth/signup", json=user)
    assert response.status_code == 201

    # login
    login_user = {
        "username_or_email": user["username"],
        "password": user["password"]
    }

    response_user = client.post('/auth/login', json=login_user)
    response_data = response_user.json()
    assert response_user.status_code == 200
    assert response_data["success"] == True
    assert response_data["code"] == 200
    assert response_data["message"] == "User successfully login"

def test_login_email_success():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "password",
        "is_active": True
    }
    response = client.post("/auth/signup", json=user)
    assert response.status_code == 201

    # login
    login_user = {
        "username_or_email": user["email"],
        "password": user["password"]
    }

    response_user = client.post('/auth/login', json=login_user)
    response_data = response_user.json()
    assert response_user.status_code == 200
    assert response_data["success"] == True
    assert response_data["code"] == 200
    assert response_data["message"] == "User successfully login"

def test_login_invalid_username():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "password",
        "is_active": True
    }
    response = client.post("/auth/signup", json=user)
    assert response.status_code == 201

    # login
    login_user = {
        "username_or_email": "Davronbek1",
        "password": user["password"]
    }

    response_user = client.post('/auth/login', json=login_user)
    assert response_user.status_code == 400

    assert response_user.json() == {
        "detail": "Invalid username or password"
    }

