from datetime import datetime

from pydantic import BaseModel, validator
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password:str
    is_active: Optional[bool]

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "username": "Davronbek",
                "email": "davronbekatadjanov@gmail.com",
                "password": "Davronbek",
                "is_active": True
            }
        }

class Login(BaseModel):
    username_or_email: str
    password: str


class SettingModel(BaseModel):
    id: Optional[int]
    currency: Optional[str]
    reminder_time: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "currency": "UZS",
                "reminder_time": 1
            }
        }
class DebtName(BaseModel):
    id: Optional[int]
    name = str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Davronbek"
            }
        }
class DebtModel(BaseModel):
    id: Optional[int]
    debt_type: Optional[str]
    name: str
    amount: float
    currency: Optional[str]
    description: Optional[str]
    received_or_given_time: Optional[datetime]
    return_time: Optional[datetime]
    setting_reminder_time_default: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "debt_type": "OWED_TO",
                "name": "Hasan",
                "amount": 13000,
                "currency": "UZS",
                "description": "Bu menda toyga deb olgan edi",
                "received_or_given_time": "2024-04-00",
                "return_time": "2024-04-2",
                "setting_reminder_time_default": False
            }
        }

    @validator("return_time", "received_or_given_time", pre=True, always=True)
    def validate_datetime_format(cls, value):
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m-%d-%Y"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise ValueError("Invalid datetime format")
        return value

class DebtUpdateModel(DebtModel):
    name: Optional[str]
    amount: Optional[float]