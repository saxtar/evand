from flask import request, jsonify, Blueprint
from . import db
from .models import Users, Events, Tickets, AlchemyEncoder, Categories
from .helper import token_required, add_cors_headers
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
@add_cors_headers
@token_required
def update_event(user, event_id):  
    err = authorize_event(user, event_id)
    if err is not None:
        return err[0], err[1]
    
    data = request.get_json()  
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
    try:
        if 'categories' in data:
            categories = data.pop('categories')
            category_list = [db.query(Categories).filter_by(name=c).first() for c in categories]
            data['categories'] = category_list
        for k, v in data.items():
            setattr(event, k, v)
        db.commit()    
        return jsonify({'message': 'event updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/events/<event_id>', methods=['DELETE'])
@add_cors_headers
@token_required
def delete_event(user, event_id):  
    err = authorize_event(user, event_id)
    if err is not None:
        return err[0], err[1]
    
    try:
        db.delete(event)  
        db.commit()    
        return jsonify({'message': 'event deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/events', methods=['POST'])
@add_cors_headers
@token_required
def create_event(user):  
    data = request.get_json()  
    err = validate_event_data(data)
    if err is not None:
        return err[0], err[1]
    
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
@add_cors_headers
def get_one_event(event_id):  
    event = db.query(Events).filter_by(id=event_id).limit(1).first()
    if event is None:
        return jsonify({'message': 'event does not exists.'}), 404
    out = {'event': json.loads(json.dumps(event, cls=AlchemyEncoder))}
    out['event']['tickets'] = json.loads(json.dumps(event.tickets, cls=AlchemyEncoder))
    out['event']['categories'] = json.loads(json.dumps(event.categories, cls=AlchemyEncoder))
    return jsonify(out), 200


@app.route('/events', methods=['GET'])
def get_all_events():  
    tags = request.args.get('tags')
    search = request.args.get('search')
    events = None
    if tags is None and search is None:
        events = db.query(Events).all() 
    elif tags is not None:
        events = db.query(Events).filter(Events.tags.contains(tags))
    else:
        events = db.query(Events).filter(Events.name.contains(search))
    event_list = []
    for e in events:
        new_e = json.loads(json.dumps(e, cls=AlchemyEncoder))
        new_e['tickets'] = json.loads(json.dumps(e.tickets, cls=AlchemyEncoder))
        event_list.append(new_e)
    return jsonify({'events': event_list}), 200

