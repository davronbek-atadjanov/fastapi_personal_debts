from datetime import datetime

from database import Base
from sqlalchemy import Column, Integer, Boolean, Text, String, Time, Float, DateTime, func

from sqlalchemy_utils import ChoiceType

class Setting(Base):
    CURRENCY_TYPES = (
        ("UZS", "uzs"),
        ("USD", "usd"),
        ("EUR", "eur")
    )

    __tablename__ = 'setting'

    id = Column(Integer, primary_key=True)
    currency = Column(ChoiceType(choices=CURRENCY_TYPES), default="UZS", nullable=False)
    reminder_time = Column(DateTime, nullable=False, default=datetime.now)

class Debt(Base):
    DEBT_STATUS = (
        ("OWED_TO", "owed_to"),
        ("OWED_by", "owed_by")
    )
    id = Column(Integer, primary_key=True)
    debt_type = Column(ChoiceType(choices=DEBT_STATUS), default='OWED_TO')
    person = Column(String)
    amount = Column(Float)
    currency = Column(ChoiceType(choices=Setting.CURRENCY_TYPES), default="UZS", nullable=False)
    description = Column(Text)
    received_or_given_time = Column(DateTime, default=func.now(),nullable=False)
    return_time = Column(DateTime, nullable=False)

