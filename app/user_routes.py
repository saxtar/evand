from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from flask import Blueprint
from . import db
from .models import Users, Events, Tickets
from .helper import token_required, gen_token, add_cors_headers


app = Blueprint('user_routes_blueprint', __name__)


@app.route('/register', methods=['POST'])
@add_cors_headers
def signup_user():  
    data = request.get_json()  
    if 'password' not in data or 'email' not in data:
        return jsonify({'message': 'user must have "email" and "password".'}), 400
    hashed_password = generate_password_hash(data['password'], method='scrypt')
    user = db.query(Users).filter_by(email=data['email']).limit(1).first()   
    if user is not None:
        return jsonify({'message': 'user already exists'}), 400
    new_user = Users(email=data['email'], password=hashed_password, admin=False)
    for k, v in data.items():
        if k != 'password':
            setattr(new_user, k, v)
    db.add(new_user)  
    db.commit()    
    return jsonify({'message': 'registeration successfully'}), 201


@app.route('/login', methods=['POST'])  
@add_cors_headers
def login_user(): 
    auth = request.get_json()   

    if not auth or 'email' not in auth or 'password' not in auth:  
        return jsonify({'message': 'user must have "email" and "password".'}), 400
    
    user = db.query(Users).filter_by(email=auth['email']).first()    
    if user is not None and check_password_hash(user.password, auth['password']):
        token = gen_token(user.email)
        return jsonify({'token' : token}), 401
    return jsonify({'message': 'could not verify'}),  401


@app.route('/users', methods=['DELETE'])
@add_cors_headers
@token_required
def delete_user(user):  
    try:
        db.delete(user)  
        db.commit()    
        return jsonify({'message': 'user deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500

