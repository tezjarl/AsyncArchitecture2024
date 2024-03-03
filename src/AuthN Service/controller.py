import json

from flask import request, jsonify
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt.exceptions import ExpiredSignatureError
from werkzeug.security import check_password_hash
from app import app, db
from kafka_producer import producer
from user import User


@app.route('/test', methods=['GET'])
def test():
    return 'Ok'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    password = data['password']

    if User.query.filter_by(username=name).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(username=name)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    try:
        user_data = {"name": new_user.name, "roles": new_user.roles}
        producer.produce('cud.auth', key=str(new_user.id), value=json.dumps(user_data))
        producer.flush()
    except Exception as e:
        print(f"Error while sending to kafka: {e}")

    return jsonify({'message': "User registered succesfully"}), 201


@app.route('/change-role', methods=['POST'])
def change_role():
    data = request.get_json()
    user_id = data['id']
    new_role = data['role']

    if new_role not in ['user', 'admin', 'manager']:
        return jsonify({'message': 'Invalid role specified'}), 400

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.roles = new_role
    db.session.commit()

    return jsonify({'message': 'Role updated successfully'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data['name']
    password = data['password']

    user = User.query.filter_by(username=name).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=name)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Incorrect username or password'}), 401


@app.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.json.get('token', None)
    try:
        with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
            verify_jwt_in_request()
        return jsonify(valid=True), 200
    except (NoAuthorizationError, ExpiredSignatureError):
        return jsonify(valid=False), 200
