from flask import request, jsonify, Blueprint
from . import db
from .models import Events, Tickets
from .helper import token_required


app = Blueprint('ticket_routes_blueprint', __name__)


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

