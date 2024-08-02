import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import User

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

def test_setting_get_success():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
    response_data = response.json()
    assert response.status_code == 201

    # login user
    login_user = {
        "username_or_email": user["username"],
        "password": user["password"]
    }
    response_user = client.post('/auth/login', json=login_user)
    response_user_data = response_user.json()
    assert response_user.status_code == 200
    access_token = response_user_data['data']['access']

    # Setting API-ga token bilan murojaat qilish
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response_setting_get = client.get('api/settings', headers=headers)
    assert response_setting_get.status_code == 200
    response_setting_data = response_setting_get.json()

    assert response_setting_data['id'] == response_data["data"]["id"]
    assert response_setting_data["username"] == response_data["data"]["username"]

    # setting bu yerda response_data user signup da kelgan data hisoblanadi
    setting = response_setting_data['setting']
    assert setting["id"] == response_data["data"]["id"]
    assert setting["currency"] == response_data["data"]["user_setting"]["currency"]
    assert setting["reminder_time"] == response_data["data"]["user_setting"]["reminder_time"]


def test_setting_all_field_update():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
    response_data = response.json()
    assert response.status_code == 201

    # login user
    login_user = {
        "username_or_email": user["username"],
        "password": user["password"]
    }
    response_user = client.post('/auth/login', json=login_user)
    response_user_data = response_user.json()
    assert response_user.status_code == 200
    access_token = response_user_data['data']['access']

    # Setting API-ga token bilan murojaat qilish
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    setting_update = {
        "currency": "USD",
        "reminder_time": 22
    }

    response_setting_update = client.put('api/settings', headers=headers, json=setting_update)
    response_setting = response_setting_update.json()
    assert response_setting_update.status_code == 200

    assert response_setting["success"] == True
    assert response_setting["code"] == 200

    setting = response_setting["setting"]
    assert setting["id"] == response_data["data"]["id"]
    assert setting["currency"] == setting_update["currency"]
    assert setting["reminder_time"] == setting_update["reminder_time"]


def test_setting_all_field_update():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
    response_data = response.json()
    assert response.status_code == 201

    # login user
    login_user = {
        "username_or_email": user["username"],
        "password": user["password"]
    }
    response_user = client.post('/auth/login', json=login_user)
    response_user_data = response_user.json()
    assert response_user.status_code == 200
    access_token = response_user_data['data']['access']

    # Setting API-ga token bilan murojaat qilish
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    setting_update = {
        "currency": "USD",
        "reminder_time": 22
    }

    response_setting_update = client.put('api/settings', headers=headers, json=setting_update)
    response_setting = response_setting_update.json()
    assert response_setting_update.status_code == 200

    assert response_setting["success"] == True
    assert response_setting["code"] == 200

    setting = response_setting["setting"]
    assert setting["id"] == response_data["data"]["id"]
    assert setting["currency"] == setting_update["currency"]
    assert setting["reminder_time"] == setting_update["reminder_time"]

def test_setting_currency_field_update():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
    response_data = response.json()
    assert response.status_code == 201

    # login user
    login_user = {
        "username_or_email": user["username"],
        "password": user["password"]
    }
    response_user = client.post('/auth/login', json=login_user)
    response_user_data = response_user.json()
    assert response_user.status_code == 200
    access_token = response_user_data['data']['access']

    # Setting API-ga token bilan murojaat qilish
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    setting_update = {
        "currency": "USD",
    }

    response_setting_update = client.put('api/settings', headers=headers, json=setting_update)
    response_setting = response_setting_update.json()
    assert response_setting_update.status_code == 200

    assert response_setting["success"] == True
    assert response_setting["code"] == 200

    setting = response_setting["setting"]
    assert setting["id"] == response_data["data"]["id"]
    assert setting["currency"] == setting_update["currency"]
    assert setting["reminder_time"] == response_data["data"]["user_setting"]["reminder_time"]

def test_setting_time_field_update():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
    response_data = response.json()
    assert response.status_code == 201

    # login user
    login_user = {
        "username_or_email": user["username"],
        "password": user["password"]
    }
    response_user = client.post('/auth/login', json=login_user)
    response_user_data = response_user.json()
    assert response_user.status_code == 200
    access_token = response_user_data['data']['access']

    # Setting API-ga token bilan murojaat qilish
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    setting_update = {
        "reminder_time": 25
    }

    response_setting_update = client.put('api/settings', headers=headers, json=setting_update)
    response_setting = response_setting_update.json()
    assert response_setting_update.status_code == 200

    assert response_setting["success"] == True
    assert response_setting["code"] == 200

    setting = response_setting["setting"]
    assert setting["id"] == response_data["data"]["id"]
    assert setting["currency"] == response_data["data"]["user_setting"]["currency"]
    assert setting["reminder_time"] == setting_update["reminder_time"]
