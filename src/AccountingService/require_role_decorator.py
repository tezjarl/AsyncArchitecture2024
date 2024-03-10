import requests
from functools import wraps
from flask import jsonify, request


def require_role(roles):
    def decorator(f):
        @wraps(f)
        def role_checker(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'msg': 'Auth header is missing'}), 401

            auth_token = auth_header.split(" ")[1]
            auth_response = requests.post('http://localhost:8085/verify-token', json={'token': auth_token})

            if auth_response.status_code != 200:
                return jsonify({'msg': 'Unauthorized'}), 401

            user_info = auth_response.json()
            user_roles = user_info['roles']
            if not set(roles) & set(user_roles):
                return jsonify({'msg': 'User doesn\'t have permisssion'}), 403
            return f(*args, **kwargs)
        return role_checker
    return decorator