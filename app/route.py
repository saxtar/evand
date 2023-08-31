import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from functools import wraps
from flask import Blueprint
from . import db
from .models import Users, Events, Tickets
from .helper import token_required, gen_token


app = Blueprint('route_blueprint', __name__)


@app.route('/register', methods=['POST'])
def signup_user():  
    data = request.get_json()  
    if 'password' not in data or 'username' not in data:
        return jsonify({'message': 'user must have "username" and "password".'}), 400
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = db.query(Users).filter_by(name=data['username']).limit(1).first()   
    if user is not None:
        return jsonify({'message': 'user already exists'}), 400
    new_user = Users(public_id=uuid.uuid4(), name=data['username'], password=hashed_password, admin=False) 
    db.add(new_user)  
    db.commit()    
    return jsonify({'message': 'registeration successfully'}), 201

@app.route('/login', methods=['POST'])  
def login_user(): 
    auth = request.get_json()   

    if not auth or 'username' not in auth or 'password' not in auth:  
        return jsonify({'message': 'user must have "username" and "password".'}), 400
    
    user = db.query(Users).filter_by(name=auth['username']).first()    
    token = gen_token(user.name, user.password, auth['password'])
    if token is not None:
        return jsonify({'token' : token}) 
    return make_response('could not verify',  401, {'Authentication': '"login required"'})

@app.route('/users/<username>', methods=['GET'])
@token_required
def get_user(username):  
    user = db.query(Users).filter_by(name=username).limit(1).first()
    if user is None:
        return jsonify({'message': 'user is not yours.'}), 400

    user_data = {}   
    user_data['username'] = user.name
    user_data['public_id'] = user.public_id
    user_data['events'] = [{'event_id': event.id} for event in db.query(Events).filter_by(author_id=user.id)]
    return jsonify({'user': user_data})

@app.route('/events/<event_id>', methods=['PUT'])
@token_required
def update_event(user, event_id):  
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
    if event is None:
        return jsonify({'message': 'event does not exists.'}), 404
    if event.author_id != user.id:
        return jsonify({'message': 'event is not yours.'}), 400
    
    data = request.get_json()  
    if 'name' not in data or 'price' not in data:
        return jsonify({'message': 'event must have "name" and "price".'}), 400

    try:
        event.name = data['name']
        event.price = data['price']
        db.commit()    
        return jsonify({'message': 'event updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/events/<event_id>', methods=['DELETE'])
@token_required
def delete_event(user, event_id):  
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
    if event is None:
        return jsonify({'message': 'event does not exists.'}), 404
    if event.author_id != user.id:
        return jsonify({'message': 'event is not yours.'}), 400
    try:
        db.delete(event)  
        db.commit()    
        return jsonify({'message': 'event deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/events', methods=['POST'])
@token_required
def create_event(user):  
    data = request.get_json()  
    if 'name' not in data or 'price' not in data:
        return jsonify({'message': 'event must have "name" and "price".'}), 400
    event = db.query(Events).filter_by(name=data['name']).limit(1).first()   
    if event is not None:
        return jsonify({'message': 'event already exists.'}), 400
    try:
        new_event = Events(name=data['name'], price=data['price'], author_id=user.id) 
        db.add(new_event)  
        db.commit()    
        db.flush()
        return jsonify({'message': 'event created successfully', 'event_id': new_event.id}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'bad parameter type.'}), 400


@app.route('/events/<event_id>', methods=['GET'])
def get_one_event(event_id):  
    event = db.query(Events).filter_by(id=event_id)
    if event is None:
        return jsonify({'message': 'event does not exists.'}), 404
    event_data = {}   
    event_data['id'] = event.id
    event_data['name'] = event.name
    event_data['price'] = event.price
    return jsonify({'event': event_data})

@app.route('/events', methods=['GET'])
def get_all_events():  
    events = db.query(Events).all() 
    result = []   
    for event in events:   
        event_data = {}   
        event_data['id'] = event.id
        event_data['name'] = event.name
        event_data['price'] = event.price
        result.append(event_data)   
    return jsonify({'events': result})


