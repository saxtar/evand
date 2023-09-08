from flask import request, jsonify, Blueprint
from . import db
from .models import Users, Events, Tickets
from .helper import token_required


app = Blueprint('event_routes_blueprint', __name__)


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


