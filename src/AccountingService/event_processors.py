import random
import json
from app import db, app
from models import Task, User, OperationType, UserOperationsLog, CompanyEarnings
from kafka_producer import get_avro_producer
from decimal import Decimal
from datetime import timedelta, datetime


def process_task_created(message_data):
    sum_to_pay = random.uniform(20,40)
    sum_to_withdraw = random.uniform(10,20)

    with app.app_context():
        user = User.query.filter_by(public_id=message_data['assigned_user_id']).first()
        if not User:
            print('User not found')
            return

        task = Task(
            public_id=message_data['task_id'],
            assigned_user_id=message_data['assigned_user_id'],
            sum_to_pay=sum_to_pay,
            sum_to_withdraw=sum_to_withdraw
        )
        db.session.add(task)
        db.session.commit()


def process_task_assigned(message_data):
    with app.app_context():
        user = User.query.filter_by(public_id=message_data['assigned_user_id']).first()
        task = Task.query.filter_by(public_id=message_data['task_id']).first()

        if user is None:
            print('User not found')
            return
        if task is None:
            print('Task not found')
            return

        user.balance -= task.sum_to_withdraw
        log = UserOperationsLog(
            user_public_id=user.public_id,
            operation_sum=task.sum_to_withdraw,
            operation_type=OperationType.BalanceDecreased,
            tasl_public_id=task.public_id
        )
        db.session.add(log)
        db.session.commit()

        analytic_task_message = {
            'public_id': task.public_id,
            'assignee_public_id': task.assigned_user_id,
            'sum_to_pay': task.sum_to_pay,
            'sum_to_withdraw': task.sum_to_withdraw
        }
        producer = get_avro_producer('analytics-task')
        producer.produce(topic='analytics.task.assigned', value=analytic_task_message)
        analytic_log_message = {
            'user_public_id': log.user_public_id,
            'operation_type': log.operation_type,
            'operation_sum': log.operation_sum,
            'operation_timestamp': log.operation_timestamp,
            'task_public_id': log.task_public_id
        }
        producer = get_avro_producer('analytics-log')
        producer.produce(topic='analytics.user.log', value=analytic_log_message)


def process_task_completed(message_data):
    with app.app_context():
        task = Task.query.filter_by(public_id=message_data['task_id']).first()
        if task is None:
            print('Task not found')
            return

        user = User.query.filter_by(public_id=task.assigned_user_id).first()
        if user is None:
            print('User not found')
            return

        user.balance += task.sum_to_pay
        log = UserOperationsLog(
            user_public_id=user.public_id,
            operation_sum=task.sum_to_pay,
            operation_type=OperationType.BalanceIncreased,
            task_public_id=task.public_id
        )
        db.session.add(log)
        db.session.commit()
        analytic_log_message = {
            'user_public_id': log.user_public_id,
            'operation_type': log.operation_type,
            'operation_sum': log.operation_sum,
            'operation_timestamp': log.operation_timestamp,
            'task_public_id': log.task_public_id
        }
        producer = get_avro_producer('analytics-log')
        producer.produce(topic='analytics.user.log', value=analytic_log_message)


def process_payments():
    with app.app_context():
        users_to_pay = User.query.filter_by(User.balance > Decimal(0)).all()
        for user in users_to_pay:
            payment_message = {
                'user_public_id': user.public_id,
                'user_email': user.email,
                'amount_to_pay': user.balance
            }
            producer = get_avro_producer('accounting-payment')
            producer.produce(topic='accounting.user.get.paid', value=payment_message)

            user.balance = Decimal('0')
            log = UserOperationsLog(
                user_public_id=user.public_id,
                operation_sum=user.balance,
                operation_type=OperationType.PaymentSucceeded
            )
            db.session.add(log)
            target_date = datetime.utcnow()
            earnings = calculate_company_earnings(target_date)
            db.session.commit()
            analytic_log_message = {
                'user_public_id': log.user_public_id,
                'operation_type': log.operation_type,
                'operation_sum': log.operation_sum,
                'operation_timestamp': log.operation_timestamp
            }
            log_producer = get_avro_producer('analytics-log')
            log_producer.produce(topic='analytics.user.log', value=analytic_log_message)
            analytic_company_earnings = {
                'date': earnings.date,
                'earnings': earnings.earnings
            }
            earning_producer = get_avro_producer('analytics-company')
            earning_producer.produce(topic='analytics.company.earnings', value=analytic_company_earnings)


def process_user_created(message_data):
    with app.app_context():
        new_user = User(
            name=message_data['name'],
            public_id=message_data['public_id'],
            balance=Decimal('0'),
            email='test@test.ru'
        )
        db.session.add(new_user)
        db.session.commit()


def calculate_company_earnings(target_date):
    start_of_day = target_date.replace(hour=0, minute=0, second=0)
    end_of_day = start_of_day + timedelta(days=1)

    assigned_tasks_sum_per_day = db.session.query(db.func.sum(UserOperationsLog.operation_sum)) \
                                     .filter(UserOperationsLog.operation_type == OperationType.BalanceDecreased,
                                             UserOperationsLog.operation_timestamp >= start_of_day,
                                             UserOperationsLog.operation_timestamp < end_of_day) \
                                     .scalar() or 0
    completed_tasks_sum_per_day = db.session.query(db.func.sum(UserOperationsLog.operation_sum)) \
                                      .filter(UserOperationsLog.operation_type == OperationType.BalanceIncreased,
                                              UserOperationsLog.operation_timestamp >= start_of_day,
                                              UserOperationsLog.operation_timestamp < end_of_day) \
                                      .scalar() or 0

    company_earnings = assigned_tasks_sum_per_day - completed_tasks_sum_per_day
    with app.app_context():
        company_earnings_entry = CompanyEarnings(
            date=start_of_day,
            earnings=company_earnings
        )
        db.session.add(company_earnings_entry)
        db.session.commit()
    return company_earnings_entry
