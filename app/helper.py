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
            return jsonify({'message': 'a valid token is missing'}), 401
        try:
            data = jwt.decode(token, secret, algorithms=["HS256"])
            user = db.query(Users).filter_by(email=data['email']).first()
            if user is None:
                return jsonify({'message': 'token is invalid'}), 401
        except jwt.ExpiredSignatureError:
            data = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_signature": False})
            user = db.query(Users).filter_by(email=data['email']).first()
            if user is None:
                return jsonify({'message': 'token is invalid'}), 401
            new_token = gen_token(user.email)
            return jsonify({'message': 'token is expired', 'new_token': new_token}), 401
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'}), 401
        return f(user, *args, **kwargs)
    return decorator

def gen_token(email):
    return jwt.encode({'email' : email, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, secret, "HS256")


def add_cors_headers(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        resp, status = f(*args, **kwargs)
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add("Access-Control-Allow-Headers", "*")
        resp.headers.add("Access-Control-Allow-Methods", "*")
        return resp, status
    return decorator
