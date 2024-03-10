import json

from flask import request, jsonify
from app import app, db
from models import User, Task, OperationType, UserOperationsLog
from datetime import datetime, timedelta
from event_processors import process_payments, calculate_company_earnings


@app.route('/balance/<user_public_id>', methods=['GET'])
def get_balance_by_user(user_public_id):
    user = User.query.filter_by(public_id=user_public_id).first()
    if user is None:
        return jsonify({'msg': 'User not found'}), 404

    operations_log = UserOperationsLog.query.filter_by(user_public_id=user_public_id).all()
    operations_response_data = [{
        'operation_type': operation.operation_type,
        'operation_sum': str(operation.operation_sum),
        'timestamp': operation.operation_timestamp.isoformat()
    } for operation in operations_log]

    return jsonify({
        'user_public_id': user_public_id,
        'current_balance': str(user.balance),
        'operations_log': operations_response_data
    }), 200


@app.route('/balance/company', methods=['GET'])
def get_company_earnings():
    date_arg = request.args.get('date')
    try:
        target_date = datetime.strptime(date_arg, '%Y-%M-%D')
    except ValueError:
        return jsonify({'msg': 'Invalid input format, date should be in YYYY-MM-DD format'}), 400

    company_earnings = calculate_company_earnings(target_date)
    return jsonify({'company_earnings': str(company_earnings)}), 200


@app.route('/balance/pay', methods=['POST'])
def make_payments():
    process_payments()
    return jsonify({'msg': 'All payments are made'}), 200



