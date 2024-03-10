from app import app
from models import db, UserLog, CompanyEarnings
from flask import request, jsonify
from sqlalchemy.sql import func
from datetime import datetime, timedelta


@app.route('/analytics/negative-balance-count', methods=['GET'])
def get_negative_balance_count():
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    users_sum_per_day = db.session.query(
        UserLog.user_public_id,
        func.sum(UserLog.operation_sum).label('total_sum')
    ).filter(
        UserLog.operation_timestamp >= start_of_day,
        UserLog.operation_timestamp < end_of_day
    ).group_by(UserLog.user_public_id).subquery()
    users_with_negative_balance_count = db.session.query(users_sum_per_day).filter(users_sum_per_day.c.total_sum < 0).count()

    return jsonify({"count": users_with_negative_balance_count}), 200


@app.route('/analytics/most-expensive-task', methods=['GET'])
def get_most_valuable_task_per_period():
    start_date = request.args.get('start-date')
    end_date = request.args.get('end-date', start_date)

    most_expensive_task_per_period = UserLog.query.filter(
        UserLog.operation_timestamp >= start_date,
        UserLog.operation_timestamp <= end_date,
        UserLog.operation_type == 1
    ).order_by(UserLog.operation_sum.desc()).first()

    if most_expensive_task_per_period:
        return jsonify({"task__public_id": most_expensive_task_per_period.task_public_id}), 200
    else:
        return jsonify({"msg": "No data for this period"}), 200


@app.route('analytics/company-earnings', methods=['GET'])
def get_company_earnings_for_today():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)
    company_earnings = CompanyEarnings.query.filter(
        CompanyEarnings.date >= today,
        CompanyEarnings.date <= today
    ).first()

    if company_earnings:
        return jsonify({"company_earnings": company_earnings.earnings}), 200
    else:
        return jsonify({"msg": "No data for today"}), 200
