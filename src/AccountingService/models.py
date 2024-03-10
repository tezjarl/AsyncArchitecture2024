from flask_sqlalchemy import SQLAlchemy
from enum import Enum, unique, IntEnum
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Numeric(10,2), nullable=False)
    email = db.Column(db.String(400), nullable=False)
    public_id = db.Column(db.String(40), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(40), nullable=True)
    assigned_user_id = db.Column(db.String(40), nullable=False)
    sum_to_pay = db.Column(db.Numeric(10,2), nullable=False)
    sum_to_withdraw = db.Column(db.Numeric(10,2), nullable=False)


class OperationType(int, Enum):
    BalanceIncreased = 1
    BalanceDecreased = 2
    PaymentSucceeded = 3


class UserOperationsLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(40), nullable=False)
    operation_type = db.Column(db.Integer, nullable=False)
    operation_sum = db.Column(db.Numeric(10, 2), nullable=False)
    operation_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    task_public_id = db.Column(db.String(40), nullable=True)


class CompanyEarnings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    earnings = db.Column(db.Numeric(10, 2), nullable=False)


