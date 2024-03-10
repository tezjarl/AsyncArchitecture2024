from flask import Flask
from models import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost:5432/myanalyticsdatabase'
db.init_app(app)

with app.app_context():
    db.create_all()


from controller import *
from kafka_consumers import start_user_log_consumer, start_task_assigned_consumer, start_task_completed_consumer, start_company_earnings_consumer


if __name__ == "__main__":
    start_user_log_consumer()
    start_task_assigned_consumer()
    start_task_completed_consumer()
    start_company_earnings_consumer()
    app.run(debug=True, host='0.0.0.0', port=8088)
