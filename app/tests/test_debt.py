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


def test_create_debt():
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
    new_debt = {
        "debt_type": "OWED_TO",
        "name": "Hasan",
        "amount": 13000,
        "currency": "UZS",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
        "setting_reminder_time_default": False
    }

    response_debt = client.post('api/debts/create', headers=headers, json=new_debt)
    response_debt_data = response_debt.json()
    assert response_debt.status_code == 201

    # ma'lumotlarni tekshiramiz
    assert response_debt_data["success"] == True
    assert response_debt_data["code"] == 201
    assert response_debt_data["message"] == "Debt is create successfully"

    # userni tekshiramiz
    user_data = response_debt_data["data"]
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user["username"]

    # debtni tekshiramiz
    debt_data = user_data["debt"]
    assert debt_data["id"] == 1
    assert debt_data["debt_type"] == new_debt["debt_type"]
    assert debt_data["name"] == new_debt["name"]
    assert debt_data["amount"] == new_debt["amount"]
    assert debt_data["currency"] == new_debt["currency"]
    assert debt_data["description"] == new_debt["description"]


def test_get_debt_by_id():
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
    # debt 1
    new_debt_1 = {
        "debt_type": "OWED_TO",
        "name": "Hasan",
        "amount": 13000,
        "currency": "UZS",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
        "setting_reminder_time_default": False
    }

    response_debt_1 = client.post('api/debts/create', headers=headers, json=new_debt_1)
    assert response_debt_1.status_code == 201
    # debt 2
    new_debt_2 = {
        "debt_type": "OWED_BY",
        "name": "Zayirbek",
        "amount": 25000,
        "currency": "UZS",
        "description": "Bu test uchun edi",
        "setting_reminder_time_default": True
    }
    response_debt_2 = client.post('api/debts/create', headers=headers, json=new_debt_2)
    assert response_debt_2.status_code == 201

    get_debt_by_id = 2
    response_get_debt = client.get(f'api/debts/{get_debt_by_id}', headers=headers)
    assert response_get_debt.status_code == 200

    response_get_data = response_get_debt.json()
    assert response_get_data["success"] == True
    assert response_get_data["code"] == 200
    assert response_get_data["message"] == f"Debt with ID {get_debt_by_id} get"

    # user check
    user_data = response_get_data["data"]
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user["username"]

    # debt check
    debt_data = user_data["debt"]
    assert debt_data["id"] == get_debt_by_id
    assert debt_data["debt_type"] == new_debt_2["debt_type"]
    assert debt_data["name"] == new_debt_2["name"]
    assert debt_data["amount"] == new_debt_2["amount"]
    assert debt_data["currency"] == new_debt_2["currency"]
    assert debt_data["description"] == new_debt_2["description"]


def test_delete_debt_by_id():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
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
    new_debt = {
        "debt_type": "OWED_TO",
        "name": "Hasan",
        "amount": 13000,
        "currency": "UZS",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
        "setting_reminder_time_default": False
    }

    response_debt = client.post('api/debts/create', headers=headers, json=new_debt)
    assert response_debt.status_code == 201
    debt_by_id = 1
    response_delete_debt = client.delete(f'api/debts/{debt_by_id}/delete', headers=headers)
    assert  response_delete_debt.status_code == 200
    response_delete_data = response_delete_debt.json()
    assert response_delete_data["success"] == True
    assert response_delete_data["code"] == 204
    assert response_delete_data["message"] == f"Debt with ID {debt_by_id} has been deleted"

    # invalid by id delete
    debt_by_id = 2
    response_delete_debt = client.delete(f'/api/debts/{debt_by_id}/delete', headers=headers)
    assert  response_delete_debt.status_code == 404
    assert response_delete_debt.json() == {
        "detail": f"This debt ID {debt_by_id} is not found"
    }


def test_update_debt_by_id():
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
    new_debt = {
        "debt_type": "OWED_TO",
        "name": "Hasan",
        "amount": 13000,
        "currency": "UZS",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
        "setting_reminder_time_default": False
    }

    response_debt = client.post('api/debts/create', headers=headers, json=new_debt)
    assert response_debt.status_code == 201

    # update api
    update_debt = {
        "debt_type": "OWED_BY",
        "amount": 20000,
        "currency": "USD",
        "description": "Bu update qilingan debt",
        "setting_reminder_time_default": True
    }
    debt_by_id = 1
    response_put_debt = client.put(f"/api/debts/{debt_by_id}/update", headers=headers, json=update_debt)
    assert response_put_debt.status_code == 200
    response_put_data = response_put_debt.json()

    assert response_put_data["success"] == True
    assert response_put_data["code"] == 200
    assert response_put_data["message"] == f"Debt with ID {debt_by_id} has been updated"

    debt_data = response_put_data["debt"]
    assert debt_data["debt_type"] == update_debt["debt_type"]
    assert debt_data["amount"] == update_debt["amount"]
    assert debt_data["currency"] == update_debt["currency"]
    assert debt_data["description"] == update_debt["description"]
    assert debt_data["setting_reminder_time_default"] == update_debt["setting_reminder_time_default"]

    debt_by_id = 2
    response_put_debt = client.put(f"/api/debts/{debt_by_id}/update", headers=headers, json=update_debt)
    assert response_put_debt.status_code == 404
    assert response_put_debt.json() == {
        "detail": f"This debt ID {debt_by_id} is not found"
    }


def test_debt_type_owed_to():
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
    new_debt_1 = {
        "debt_type": "OWED_TO",
        "name": "Hasan",
        "amount": 13000,
        "currency": "UZS",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
        "setting_reminder_time_default": False
    }
    # debt 1
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_1)
    assert response_debt.status_code == 201

    new_debt_2 = {
        "debt_type": "OWED_TO",
        "name": "Hasan",
        "amount": 130,
        "currency": "USD",
        "description": "Test uchun deb olgan edi",
        "setting_reminder_time_default": True
    }
    # debt 2
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_2)
    assert response_debt.status_code == 201

    # owed_to api ni tekshiramiz

    response_owed_to = client.get('/api/debts/?debt_type=owed_to', headers=headers)
    assert response_owed_to.status_code == 200
    response_owed_to_data = response_owed_to.json()
    # 1 chi debt
    owed_to_data_1 = response_owed_to_data[0]

    # userni tekshiramiz
    user_data = owed_to_data_1["user"]
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user["username"]

    # debtni tekshiramiz

    debt_data_1 = owed_to_data_1["debt"]
    assert debt_data_1["id"] == 1
    assert debt_data_1["debt_type"] == new_debt_1["debt_type"]
    assert debt_data_1["name"] == new_debt_1["name"]
    assert debt_data_1["amount"] == new_debt_1['amount']
    assert debt_data_1["currency"] == new_debt_1["currency"]

     # 2 chi debt
    owed_to_data_2 = response_owed_to_data[1]

    # userni tekshiramiz
    user_data = owed_to_data_2["user"]
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user["username"]

    # debtni tekshiramiz
    debt_data_2 = owed_to_data_2["debt"]
    assert debt_data_2["id"] == 2
    assert debt_data_2["debt_type"] == new_debt_2["debt_type"]
    assert debt_data_2["name"] == new_debt_2["name"]
    assert debt_data_2["amount"] == new_debt_2['amount']
    assert debt_data_2["currency"] == new_debt_2["currency"]

def test_debt_type_owed_by():
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
    new_debt_1 = {
        "debt_type": "OWED_BY",
        "name": "Davronbek",
        "amount": 1600,
        "currency": "USD",
        "description": "Test uchun deb olgan edi",
        "setting_reminder_time_default": True
    }
    # debt 1
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_1)
    assert response_debt.status_code == 201

    new_debt_2 = {
        "debt_type": "OWED_BY",
        "name": "Davronbek",
        "amount": 19000,
        "currency": "USD",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
    }
    # debt 2
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_2)
    assert response_debt.status_code == 201

    # owed_by api ni tekshiramiz

    response_owed_by = client.get('/api/debts/?debt_type=owed_by', headers=headers)
    assert response_owed_by.status_code == 200
    response_owed_by_data = response_owed_by.json()
    # 1 chi debt
    owed_by_data_1 = response_owed_by_data[0]

    # userni tekshiramiz
    user_data = owed_by_data_1["user"]
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user["username"]

    # debtni tekshiramiz

    debt_data_1 = owed_by_data_1["debt"]
    assert debt_data_1["id"] == 1
    assert debt_data_1["debt_type"] == new_debt_1["debt_type"]
    assert debt_data_1["name"] == new_debt_1["name"]
    assert debt_data_1["amount"] == new_debt_1['amount']
    assert debt_data_1["currency"] == new_debt_1["currency"]

    # 2 chi debt
    owed_by_data_2 = response_owed_by_data[1]

    # userni tekshiramiz
    user_data = owed_by_data_2["user"]
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user["username"]

    # debtni tekshiramiz
    debt_data_2 = owed_by_data_2["debt"]
    assert debt_data_2["id"] == 2
    assert debt_data_2["debt_type"] == new_debt_2["debt_type"]
    assert debt_data_2["name"] == new_debt_2["name"]
    assert debt_data_2["amount"] == new_debt_2['amount']
    assert debt_data_2["currency"] == new_debt_2["currency"]


def test_debt_type_individual():
    user = {
        "username": "Davronbek",
        "email": "davronbek@gmail.com",
        "password": "Davronbek",
        "is_active": True
    }
    response = client.post('/auth/signup', json=user)
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
    new_debt_1 = {
        "debt_type": "OWED_TO",
        "name": "Davronbek",
        "amount": 16000,
        "currency": "USD",
        "description": "Test uchun deb olgan edi",
        "setting_reminder_time_default": True
    }
    # debt 1
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_1)
    assert response_debt.status_code == 201

    new_debt_2 = {
        "debt_type": "OWED_BY",
        "name": "Davronbek",
        "amount": 19000,
        "currency": "USD",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
    }
    # debt 2
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_2)
    assert response_debt.status_code == 201
    new_debt_3 = {
        "debt_type": "OWED_BY",
        "name": "Hasan",
        "amount": 25000,
        "currency": "UZS",
        "description": "Bu menda toyga deb olgan edi",
        "setting_reminder_time_default": True
    }
    # debt 3
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_3)
    assert response_debt.status_code == 201

    response_individual = client.get('/api/debts/?debt_type=individual', headers=headers)
    assert response_individual.status_code == 200
    response_individual_data = response_individual.json()

    individual_data_1 = response_individual_data[0]
    assert individual_data_1['debt_name_id'] == 1
    assert individual_data_1['name'] == new_debt_1['name']
    assert individual_data_1['owed_to_money'] == new_debt_1['amount']
    assert individual_data_1['owed_by_money'] == new_debt_2['amount']
    assert individual_data_1['total'] == float(new_debt_1['amount'] - new_debt_2['amount'])

    individual_data_2 = response_individual_data[1]
    assert individual_data_2['debt_name_id'] == 2
    assert individual_data_2['name'] == new_debt_3['name']
    assert individual_data_2['owed_to_money'] == 0
    assert individual_data_2['owed_by_money'] == new_debt_3['amount']
    assert individual_data_2['total'] == float(0 - new_debt_3['amount'])


def test_debt_individual_by_id():
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
    new_debt_1 = {
        "debt_type": "OWED_TO",
        "name": "Davronbek",
        "amount": 16000,
        "currency": "USD",
        "description": "Test uchun deb olgan edi",
        "setting_reminder_time_default": True
    }
    # debt 1
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_1)
    assert response_debt.status_code == 201

    new_debt_2 = {
        "debt_type": "OWED_BY",
        "name": "Davronbek",
        "amount": 19000,
        "currency": "USD",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
    }
    # debt 2
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_2)
    assert response_debt.status_code == 201

    debt_name_by_id = 1
    response_individual_data = client.get(f'api/debts/individual/{debt_name_by_id}', headers=headers)
    assert response_individual_data.status_code == 200
    response_data_individual = response_individual_data.json()

    # debt 1
    individual_data_1 = response_data_individual[0]
    debt_data = individual_data_1["debt"]
    assert debt_data["id"] == 1
    assert debt_data["debt_type"] == new_debt_1["debt_type"]
    assert debt_data["name"] == new_debt_1["name"]
    assert debt_data["amount"] == new_debt_1["amount"]
    assert debt_data["currency"] == new_debt_1["currency"]

    # debt 2
    individual_data_2 = response_data_individual[1]
    debt_data = individual_data_2["debt"]
    assert debt_data["id"] == 2
    assert debt_data["debt_type"] == new_debt_2["debt_type"]
    assert debt_data["name"] == new_debt_2["name"]
    assert debt_data["amount"] == new_debt_2["amount"]
    assert debt_data["currency"] == new_debt_2["currency"]


def test_monitoring_debts():
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
    new_debt_1 = {
        "debt_type": "OWED_TO",
        "name": "Davronbek",
        "amount": 16000,
        "currency": "USD",
        "description": "Test uchun deb olgan edi",
        "setting_reminder_time_default": True
    }
    # debt 1
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_1)
    assert response_debt.status_code == 201

    new_debt_2 = {
        "debt_type": "OWED_BY",
        "name": "Davronbek",
        "amount": 19000,
        "currency": "USD",
        "description": "Bu menda toyga deb olgan edi",
        "return_time": "2024-04-2",
    }
    # debt 2
    response_debt = client.post('api/debts/create', headers=headers, json=new_debt_2)
    assert response_debt.status_code == 201

    response_monitoring = client.get('api/monitoring', headers=headers)
    assert response_monitoring.status_code == 200
    response_monitoring_data = response_monitoring.json()
    user_data = response_monitoring_data["user"]

    # user check
    assert user_data["id"] == response_data["data"]["id"]
    assert user_data["username"] == user['username']

    # debt check
    debt_monitoring = response_monitoring_data["debt_monitoring"]
    assert debt_monitoring["owed_to_total"] == new_debt_1["amount"]
    assert debt_monitoring["owed_by_total"] == new_debt_2["amount"]
    assert debt_monitoring["total"] == new_debt_1["amount"] - new_debt_2["amount"]
