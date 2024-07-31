from sqlalchemy import Column, Integer, Boolean, Text, String, Float, DateTime, func, ForeignKey
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(70), unique=True)
    password = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)

    setting = relationship('Setting', back_populates='user', uselist=False,  cascade='all, delete-orphan') # One-to-One
    debts = relationship('Debt', back_populates='user',  cascade='all, delete-orphan') # One-to-Many

class Setting(Base):
    CURRENCY_TYPES = (
        ("UZS", "uzs"),
        ("USD", "usd"),
        ("EUR", "eur")
    )

    __tablename__ = 'setting'
    id = Column(Integer, primary_key=True)
    currency = Column(ChoiceType(choices=CURRENCY_TYPES), default="UZS")
    reminder_time = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='setting')  # One-to-One munosabat


class DebtName(Base):
    __tablename__ = 'debtname'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Bog'lanishlar
    debts = relationship('Debt', back_populates='debtname')  # One-to-Many munosabat


class Debt(Base):
    DEBT_STATUS = (
        ("OWED_TO", "owed_to"),
        ("OWED_BY", "owed_by")
    )
    __tablename__ = 'debt'
    id = Column(Integer, primary_key=True)
    debt_type = Column(ChoiceType(choices=DEBT_STATUS), default='OWED_TO')
    name_id = Column(Integer, ForeignKey('debtname.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(ChoiceType(choices=Setting.CURRENCY_TYPES), default=Setting.currency)
    description = Column(Text, nullable=True)
    received_or_given_time = Column(DateTime, default=func.now(), nullable=True)
    return_time = Column(DateTime, nullable=True)
    setting_reminder_time_default = Column(Boolean, default=False, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))  # ForeignKey to User
    # Bog'lanishlar
    debtname = relationship('DebtName', back_populates='debts')  # Many-to-One munosabat

    # User bilan munosabat

    user = relationship('User', foreign_keys=[user_id], back_populates='debts', lazy='joined')