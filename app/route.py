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
    if user is not None and check_password_hash(user.password, auth['password']):
        token = gen_token(user.name)
        return jsonify({'token' : token}) 
    return make_response('could not verify',  401, {'Authentication': '"login required"'})

@app.route('/users', methods=['GET'])
@token_required
def get_user(user):  
    user_data = {}   
    user_data['username'] = user.name
    user_data['public_id'] = user.public_id
    user_data['events'] = [{'event_id': event.id} for event in db.query(Events).filter_by(author_id=user.id)] 
    user_data['tickets'] = [{'ticket_id': ticket.id} for ticket in db.query(Tickets).filter_by(buyer_id=user.id)]
    return jsonify({'user': user_data})

@app.route('/users', methods=['DELETE'])
@token_required
def delete_user(user):  
    try:
        db.delete(user)  
        db.commit()    
        return jsonify({'message': 'user deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500

@app.route('/tickets/<ticket_id>', methods=['GET'])
@token_required
def get_ticket(user, ticket_id):  
    ticket = db.query(Tickets).filter_by(id=ticket_id, buyer_id=user.id).limit(1).first()
    if ticket is None:
        return jsonify({'message': 'ticket not found.'}), 404

    ticket_data = {}   
    ticket_data['buyer_username'] = user.name
    ticket_data['event_id'] = ticket.event_id
    ticket_data['is_paid'] = ticket.is_paid
    return jsonify({'ticket': ticket_data})

@app.route('/tickets/<ticket_id>', methods=['DELETE'])
@token_required
def delete_ticket(user, ticket_id):  
    ticket = db.query(Tickets).filter_by(id=ticket_id).limit(1).first()
    if ticket is None:
        return jsonify({'message': 'ticket does not exists.'}), 404
    if ticket.buyer_id != user.id:
        return jsonify({'message': 'ticket is not yours.'}), 400
    try:
        db.delete(ticket)  
        db.commit()    
        return jsonify({'message': 'ticket deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500

@app.route('/tickets/<ticket_id>', methods=['PUT'])
@token_required
def purchase_ticket(user, ticket_id):  
    data = request.get_json()  
    if 'purchase_id' not in data:
        return jsonify({'message': 'ticket purchase must have "purchase_id".'}), 400
    ticket = db.query(Tickets).filter_by(id=ticket_id).limit(1).first()   
    if ticket is None:
        return jsonify({'message': 'ticket does not exists.'}), 404
    try:
        ticket.is_paid = True 
        db.commit()    
        db.flush()
        return jsonify({'message': 'ticket purchased successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'something went wrong.'}), 500



@app.route('/tickets', methods=['POST'])
@token_required
def create_ticket(user):  
    data = request.get_json()  
    if 'event_id' not in data:
        return jsonify({'message': 'ticket must have "event_id".'}), 400
    event = db.query(Events).filter_by(id=data['event_id']).limit(1).first()   
    if event is None:
        return jsonify({'message': 'event does not exists.'}), 404
    try:
        new_ticket = Tickets(event_id=event.id, buyer_id=user.id) 
        db.add(new_ticket)  
        db.commit()    
        db.flush()
        return jsonify({'message': 'ticket created successfully', 'ticket_id': new_ticket.id}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'bad parameter type.'}), 400


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
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
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


