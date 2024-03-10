from flask import Flask
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost:5432/mytaskdatabase'
db.init_app(app)


with app.app_context():
    db.create_all()


from controller import *
from kafka_consumer import start_consumer_thread


if __name__ == "__main__":
    start_consumer_thread()
    app.run(debug=True, host='0.0.0.0', port=8086)
