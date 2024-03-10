from confluent_kafka.avro import AvroConsumer
from threading import Thread
from app import db, app
from models import Task, UserLog, CompanyEarnings


def get_avro_consumer(topic):
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'analytic-consumer',
        'auto.offset.reset': 'earliest',
        'schema.registry.url': 'http://localhost:8081'
    }
    consumer = AvroConsumer(consumer_config)
    consumer.subscribe([topic])
    return consumer


def task_assigned_consume():
    consumer = get_avro_consumer('analytics.task.assigned')

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')

            message_data = message.value()
            new_task = Task(
                public_id=message_data['public_id'],
                assignee_public_id=message_data['assignee_public_id'],
                sum_to_pay=message_data['sum_to_pay'],
                sum_to_withdraw=message_data['sum_to_withdraw'],
                is_completed=False
            )
            with app.app_context():
                db.session.add(new_task)
                db.session.commit()
    finally:
        consumer.close()


def task_completed_consume():
    consumer = get_avro_consumer('task.completed')

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')

            message_data = message.value()
            with app.app_context():
                completed_task = Task.query.filter_by(public_id=message_data['task_id'])
                completed_task.is_completed = True
                db.session.commit()
    finally:
        consumer.close()


def user_log_consume():
    consumer = get_avro_consumer('analytics.user.log')
    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')

            message_data = message.value()
            log = UserLog(
                user_public_id=message_data['user_public_id'],
                operation_type=message_data['operation_type'],
                operation_sum=message_data['operation_sum'],
                operation_timestamp=message_data['operation_timestamp']
            )
            with app.app_context():
                db.session.add(log)
                db.session.commit()
    finally:
        consumer.close()


def company_earnings_consume():
    consumer = get_avro_consumer('analytics.company.earnings')
    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')

            message_data = message.value()
            earnings = CompanyEarnings(
                date=message_data['date'],
                earnings=message_data['earnings']
            )
            with app.app_context():
                db.session.add(earnings)
                db.session.commit()
    finally:
        consumer.close()


def start_task_assigned_consumer():
    consumer_thread = Thread(target=task_assigned_consume)
    consumer_thread.daemon = True
    consumer_thread.start()


def start_task_completed_consumer():
    consumer_thread = Thread(target=task_completed_consume)
    consumer_thread.daemon = True
    consumer_thread.start()


def start_user_log_consumer():
    consumer_thread = Thread(target=user_log_consume)
    consumer_thread.daemon = True
    consumer_thread.start()


def start_company_earnings_consumer():
    consumer_thread = Thread(target=company_earnings_consume)
    consumer_thread.daemon = True
    consumer_thread.start()
