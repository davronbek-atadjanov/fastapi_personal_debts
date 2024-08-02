import datetime

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import or_
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.schemas import SignUpModel, Login
from app.models import User, Setting
from app.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(
    prefix='/auth'
)
@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel, session: Session = Depends(get_db)):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active
    )
    session.add(new_user)
    session.commit()

    new_user_setting = Setting(
        user_id=new_user.id
    )
    session.add(new_user_setting)
    session.commit()

    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "user_setting": {
            "id": new_user.setting.id,
            "currency": new_user.setting.currency.code,
            "reminder_time": new_user.setting.reminder_time
        }
    }
    response_data = {
        "success": True,
        "status": 201,
        "message": "User is created successfully",
        "data": data
    }
    return response_data


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user: Login, Authorize: AuthJWT=Depends(), session: Session = Depends(get_db)):
    db_user = session.query(User).filter(
        or_(User.username == user.username_or_email,
            User.email == user.username_or_email
            )
    ).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_lifetime = datetime.timedelta(minutes=60)
        refresh_lifetime = datetime.timedelta(days=3)
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)

        token = {
            "access": access_token,
            "refresh": refresh_token
        }

        response = {
            "success": True,
            "code": 200,
            "message": "User successfully login",
            "data": token
        }

        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

