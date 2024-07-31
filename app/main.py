from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from app.routers.setting_routes import setting_router
from app.routers.auth_routes import auth_router
from app.routers.debt_routes import debt_router

app = FastAPI()


class Settings(BaseModel):
    authjwt_secret_key: str = 'e9aea1f6d5aff0651e1e39cb64419353ceaf7fc57d978afe9b83299bd3a641fd'

@AuthJWT.load_config
def get_config():
    return Settings()



app.include_router(setting_router)
app.include_router(auth_router)
app.include_router(debt_router)

