from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from functools import wraps
from flask import Blueprint
from . import db
from .models import Users, Events, Tickets
from .helper import token_required, gen_token


app = Blueprint('user_routes_blueprint', __name__)


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

