from flask import request, jsonify, Blueprint
from . import db
from .models import Users, Events, Tickets, AlchemyEncoder, Categories
from .helper import token_required
import json


app = Blueprint('event_routes_blueprint', __name__)


def validate_event_data(data):
    if 'name' not in data:
        return (jsonify({'message': 'event must have "name".'}), 400)
    event = db.query(Events).filter_by(name=data['name']).limit(1).first()
    if event is not None:
        return (jsonify({'message': 'event name already exists.'}), 400)
    if 'categories' in data:
        for c in data['categories']:
            category = db.query(Categories).filter_by(name=c).first()
            if category is None:
                return (jsonify({'message': f'the \"{c}\" not found in categories.'}), 400)

    return None


def authorize_event(user, event_id):
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
    if event is None:
        return (jsonify({'message': 'event does not exists.'}), 404)
    if event.author_id != user.id:
        return (jsonify({'message': 'event is not yours.'}), 403)
    return None


@app.route('/events/<event_id>', methods=['PUT'])
@token_required
def update_event(user, event_id):  
    err = authorize_event(user, event_id)
    if err is not None:
        return err
    
    data = request.get_json()  
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
    try:
        for k, v in data.items():
            setattr(event, k, v)
        db.commit()    
        return jsonify({'message': 'event updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/events/<event_id>', methods=['DELETE'])
@token_required
def delete_event(user, event_id):  
    err = authorize_event(user, event_id)
    if err is not None:
        reutrn *err
    
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
    err = validate_event_data(data)
    if err is not None:
        return err    
    
    try:
        if 'categories' in data:
            categories = data.pop('categories')
            category_list = [db.query(Categories).filter_by(name=c).first() for c in categories]
            data['categories'] = category_list
        new_event = Events(**data) 
        new_event.author_id = user.id
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
    out = {'event': json.loads(json.dumps(event, cls=AlchemyEncoder))}
    out['event']['tickets'] = json.loads(json.dumps(event.tickets, cls=AlchemyEncoder))
    out['event']['categories'] = json.loads(json.dumps(event.categories, cls=AlchemyEncoder))
    return jsonify(out)


@app.route('/events', methods=['GET'])
def get_all_events():  
    events = db.query(Events).all() 
    return jsonify({'events': [json.loads(json.dumps(e, cls=AlchemyEncoder)) for e in events]})


