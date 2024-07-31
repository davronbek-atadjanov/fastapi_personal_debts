from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, status, Depends
from fastapi_jwt_auth import AuthJWT

from app.database import session
from app.models import Setting, User
from app.schemas import SettingModel

setting_router = APIRouter(
    prefix='/api/settings'
)

@setting_router.get('/', status_code=status.HTTP_200_OK)
async def setting_get(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with username not found")

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    setting = session.query(Setting).filter(Setting.user_id == current_user.id).first()

    if setting:
        data = {
            "id": current_user.id,
            "username": current_user.username,
            "setting": {
                "id": setting.id,
                "currency": setting.currency.value,
                "reminder_time": setting.reminder_time
            }
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User setting not found")


@setting_router.put("/", status_code=status.HTTP_200_OK)
async def update_setting(update_data: SettingModel, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with username not found")

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    setting = session.query(Setting).filter(Setting.user_id == current_user.id).first()
    if setting:
        if update_data.currency is not None:
            setting.currency = update_data.currency

        if update_data.reminder_time is not None:
            setting.reminder_time = update_data.reminder_time

        session.commit()
        data = {
            "success": True,
            "code": 200,
            "message": f"{username} with setting update",
            "setting": {
                "id": setting.id,
                "currency": setting.currency,
                "reminder_time": setting.reminder_time
            }
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User setting not found")

