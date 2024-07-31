from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, status, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from app.models import User, DebtName, Debt, Setting
from app.schemas import DebtModel, DebtUpdateModel
from fastapi_jwt_auth import AuthJWT
from app.database import session

debt_router = APIRouter(
    prefix="/api/debts"
)

@debt_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_debt(debt_data: DebtModel, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    setting = session.query(Setting).filter(Setting.user_id == current_user.id).first()
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    current_debtname = session.query(DebtName).filter(DebtName.name == debt_data.name).first()

    if current_debtname is not None:
        name_id = current_debtname.id
    else:
        new_debtname = DebtName(
            name=str(debt_data.name)

        )
        session.add(new_debtname)
        session.commit()
        name_id = new_debtname.id

    if debt_data.return_time is not None:
        return_time = debt_data.return_time
    else:
        if debt_data.setting_reminder_time_default:
            current_time = datetime.now()
            delta = timedelta(days=setting.reminder_time)
            return_time = current_time + delta
        else:
            return_time = None

    new_debt = Debt(
        user_id=current_user.id,
        debt_type=debt_data.debt_type,
        name_id=name_id,
        amount=float(debt_data.amount),
        currency=debt_data.currency,
        description=debt_data.description,
        return_time=return_time,
        setting_reminder_time_default=debt_data.setting_reminder_time_default
    )
    session.add(new_debt)
    session.commit()
    data = {
        "id": new_debt.user.id,
        "username": new_debt.user.username,
        "debt": {
            "id": new_debt.id,
            "debt_type": new_debt.debt_type.value,
            "name": new_debt.debtname.name,
            "amount": new_debt.amount,
            "currency": new_debt.currency.value,
            "description": new_debt.description,
            "received_or_given_time": new_debt.received_or_given_time,
            "return_time": new_debt.return_time
        }
    }
    response = {
        "success": True,
        "code": 201,
        "message": "Debt is create successfully",
        "data": data
    }
    return jsonable_encoder(response)

@debt_router.delete('/{id}/delete', status_code=status.HTTP_200_OK)
async def delete_debt_by_id(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.get_raw_jwt()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    debt = session.query(Debt).filter( Debt.id == id, Debt.user_id == current_user.id).first()
    debt_name_user = debt.debtname.name
    if debt:
        session.delete(debt)
        session.commit()

        # DebtName obektini o'chirish
        debtname = session.query(DebtName).filter(DebtName.name == debt_name_user).first()
        if debtname:
            debts_count = session.query(Debt).filter(Debt.name_id == debtname.id).count()
            if debts_count == 0:
                session.delete(debtname)
                session.commit()
        data = {
            "success": True,
            "code": 204,
            "message": f"Debt with ID {id} has been deleted"
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This debt ID {id} is not found")


@debt_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_debt_by_id(id:int, update_data: DebtUpdateModel, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    debt = session.query(Debt).filter(Debt.id == id, Debt.user_id == current_user.id).first()

    if debt:
        debtname = session.query(DebtName).filter(DebtName.name == debt.debtname.name).first()
        setting = session.query(Setting).filter(Setting.user_id == current_user.id).first()
        # update debt name
        if update_data.name is not None:
            debtname.name = update_data.name
            debtname_check = session.query(DebtName).filter(DebtName.name == debtname.name).first()
            if debtname_check is None:
                new_debtname = DebtName(
                    name=debtname.name
                )
                session.add(new_debtname)
                session.commit()

        # update return_time
        if update_data.return_time is not None:
            debt.return_time = update_data.return_time
        else:
            if update_data.setting_reminder_time_default:
                current_time = datetime.now()
                delta = timedelta(days=setting.reminder_time)
                debt.return_time = current_time + delta

        # all update items
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(debt, key, value)
        session.commit()

        data = {
            "success": True,
            "code": 200,
            "message": f"Debt with ID {id} has been updated",
            "debt": {
                "id": debt.id,
                "debt_type": debt.debt_type,
                "name": debt.debtname.name,
                "amount": debt.amount,
                "currency": debt.currency,
                "description": debt.description,
                "received_or_given_time": debt.received_or_given_time,
                "return_time": debt.return_time,
                "setting_reminder_time_default": debt.setting_reminder_time_default
            }
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This debt ID {id} is not found")


@debt_router.get("/", status_code=status.HTTP_200_OK)
async def debt_type_debt_all(debt_type: Optional[str] = Query(None), Authorize: AuthJWT=Depends()):
    """debt_type=(owed_to, owed_by, individual): /api/debts/?debt_type=owed_to """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()


    if debt_type != 'individual':
        if debt_type == "owed_to":
            debt_type_code = "OWED_TO"
        elif debt_type == "owed_by":
            debt_type_code = "OWED_BY"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid debt_type")

        debts = session.query(Debt).filter(
            Debt.user_id == current_user.id,
            Debt.debt_type == debt_type_code
        ).all()

        if not debts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No debts found")
        custom_data = [
            {
                "user": {
                    "id": debt.user.id,
                    "username": debt.user.username
                },
                "debt": {
                    "id": debt.id,
                    "debt_type": debt.debt_type,
                    "name": debt.debtname.name,
                    "amount": debt.amount,
                    "currency": debt.currency,
                    "received_or_given_time": debt.received_or_given_time,
                    "return_time": debt.return_time,
                }
            } for debt in debts
        ]
        return jsonable_encoder(custom_data)

    elif debt_type == 'individual':
        debt_names = session.query(DebtName).all()
        custom_data = []
        for debt_name in debt_names:
            owed_to_money = 0
            owed_by_money = 0
            debts = session.query(Debt).filter(Debt.name_id == debt_name.id, Debt.user_id == current_user.id).all()
            for debt in debts:
                if debt.debt_type == 'OWED_TO':
                    owed_to_money += debt.amount
                else:
                    owed_by_money += debt.amount

            data = {
                "debt_name_id": debt_name.id,
                "name": debt_name.name,
                "owed_to_money": owed_to_money,
                "owed_by_money": owed_by_money,
                "total": owed_to_money - owed_by_money
            }
            custom_data.append(data)
        return jsonable_encoder(custom_data)

@debt_router.get('/individual/{id}', status_code=status.HTTP_200_OK)
async def individual_debtname_by_id(id:int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    debtname = session.query(DebtName).filter(DebtName.id == id).first()
    if not debtname:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DebtName with Id {id} not found")

    debts = session.query(Debt).filter(Debt.user_id == current_user.id, Debt.name_id == debtname.id ).all()

    if debts:
        custom_data = [
            {
                "user": {
                    "id": debt.user.id,
                    "username": debt.user.username
                },
                "debt": {
                    "id": debt.id,
                    "debt_type": debt.debt_type.value,
                    "name": debt.debtname.name,
                    "amount": debt.amount,
                    "currency": debt.currency.value,
                    "received_or_given_time": debt.received_or_given_time,
                    "return_time": debt.return_time,
                }
            } for debt in debts
        ]
        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No debts found")
