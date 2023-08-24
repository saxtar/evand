import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
from flask import Blueprint
from . import db
from .models import Users
from .helper import token_required


app = Blueprint('route_blueprint', __name__)


@app.route('/register', methods=['POST'])
def signup_user():  
    data = request.get_json()  
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = db.query(Users).filter_by(name=data['name']).limit(1).first()   
    if user is not None:
        return jsonify({'message': 'user already exists'}), 400
    new_user = Users(public_id=uuid.uuid4(), name=data['name'], password=hashed_password, admin=False) 
    db.add(new_user)  
    db.commit()    
    return jsonify({'message': 'registeration successfully'}), 201

@app.route('/login', methods=['POST'])  
def login_user(): 
    auth = request.authorization   

    if not auth or not auth.username or not auth.password:  
        return make_response('could not verify', 401, {'Authentication': 'login required"'})    

    user = db.query(Users).filter_by(name=auth.username).first()   
     
    if check_password_hash(user.password, auth.password):

        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
        return jsonify({'token' : token}) 

    return make_response('could not verify',  401, {'Authentication': '"login required"'})

@app.route('/users', methods=['GET'])
def get_all_users():  
    users = db.query(Users).all() 
    result = []   
    for user in users:   
        user_data = {}   
        user_data['public_id'] = user.public_id  
        user_data['name'] = user.name 
        user_data['password'] = user.password
        user_data['admin'] = user.admin 
        result.append(user_data)   
    return jsonify({'users': result})

