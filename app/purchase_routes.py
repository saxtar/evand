from flask import request, jsonify, Blueprint
from . import db
from .models import Purchases, Tickets
from .helper import token_required, add_cors_headers


app = Blueprint('purchase_routes_blueprint', __name__)


def validate_purchase_data(data):
    if not all(k in data for k in ('ticket_id')):
        return (jsonify({'message': 'purchase must have "ticket_id".'}), 400)
    ticket = db.query(Tickets).filter_by(id=data['ticket_id']).limit(1).first()   
    if ticket is None:
        return (jsonify({'message': 'ticket does not exists.'}), 404)
    return None


def authorize_purchase(user, purchase_id):
    purchase = db.query(Purchases).filter_by(id=purchase_id).limit(1).first()
    if purchase is None:
        return (jsonify({'message': 'purchase does not exists.'}), 404)
    if purchase.buyer_id != user.id:
        return (jsonify({'message': 'purchase is not yours.'}), 400)
    return None


@app.route('/purchases/<purchase_id>', methods=['GET'])
@add_cors_headers
@token_required
def get_purchase(user, purchase_id):  
    err = authorize_purchase(user, purchase_id)
    if err is not None:
        return err
    
    purchase = db.query(Purchases).filter_by(id=purchase_id, buyer_id=user.id).limit(1).first()
    return jsonify({'ticket': purchase}), 200


@app.route('/purchases/<purchase_id>', methods=['DELETE'])
@add_cors_headers
@token_required
def delete_purchase(user, purchase_id):  
    err = authorize_purchase(user, purchase_id)
    if err is not None:
        return err

    purchase = db.query(Purchases).filter_by(id=purchase_id, buyer_id=user.id).limit(1).first()
    try:
        db.delete(purchase)  
        db.commit()    
        return jsonify({'message': 'purchase deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/purchases/<purchase_id>', methods=['PUT'])
@add_cors_headers
@token_required
def pay_purchase(user, purchase_id):  
    data = request.get_json()  
    err = validate_purchase_data(data) 
    if err is not None:
        return err

    err = authorize_purchase(user, purchase_id)
    if err is not None:
        return err
    
    purchase = db.query(Purchases).filter_by(id=purchase_id, buyer_id=user.id).limit(1).first()
    try:
        purchase.is_paid = True 
        db.commit()    
        db.flush()
        return jsonify({'message': 'purchase paid successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'something went wrong.'}), 500


@app.route('/purchases', methods=['POST'])
@add_cors_headers
@token_required
def create_purchase(user):  
    data = request.get_json()
    err = validate_purchase_data(data) 
    if err is not None:
        return err
    try:
        new_purchase = Purchases(**data) 
        db.add(new_purchase)  
        db.commit()    
        db.flush()
        return jsonify({'message': 'purchase created successfully', 'purchase_id': new_purchase.id}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'bad parameter type.'}), 400

