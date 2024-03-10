from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_public_id = db.Column(db.String(40), unique=True, nullable=False)
    operation_type = db.Column(db.Integer, nullable=False)
    operation_sum = db.Column(db.Numeric(10, 2), nullable=False)
    operation_timestamp = db.Column(db.DateTime, nullable=False)
    task_public_id = db.Column(db.String(40), nullable=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(40), unique=True, nullable=False)
    assignee_public_id = db.Column(db.String(40), unique=True, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    sum_to_pay = db.Column(db.Numeric(10, 2), nullable=False)
    sum_to_withdraw = db.Column(db.Numeric(10, 2), nullable=False)


class CompanyEarnings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    earnings = db.Column(db.Numeric(10, 2), nullable=False)
