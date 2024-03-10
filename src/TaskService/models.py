from flask_sqlalchemy import SQLAlchemy
import shortuuid

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    public_id = db.Column(db.String(40), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(40), nullable=False, default=shortuuid.uuid)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    assignee_public_id = db.Column(db.String(40), nullable=False)
