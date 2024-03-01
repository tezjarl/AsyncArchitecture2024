from datetime import timedelta
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost:5432/mydatabase'
app.config['JWT_SECRET_KEY'] = 'my_super_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
db = SQLAlchemy(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()


from controller import *


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8085)
