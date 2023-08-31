from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import datetime

from . import secret, db
from .models import Users


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if request.headers.get('Authorization') is not None:
            token = request.headers['Authorization']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, secret, algorithms=["HS256"])
            current_user = db.query(Users).filter_by(name=data['username']).first()
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorator

def gen_token(user_name, user_password, auth_password):
    if check_password_hash(user_password, auth_password):
        return jwt.encode({'username' : user_name, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, secret, "HS256")
    return None
