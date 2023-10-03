from flask import request, jsonify, Blueprint
from . import db, purchase_api_key, host_url
from .models import Purchases, Tickets, AlchemyEncoder
from .helper import token_required, add_cors_headers
import json


app = Blueprint('purchase_routes_blueprint', __name__)


def validate_purchase_data(data):
    if 'ticket_id' not in data:
        return (jsonify({'message': 'purchase must have "ticket_id".'}), 400)
    if 'is_paid' in data:
        return (jsonify({'message': 'invalid data".'}), 400)
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
    return jsonify({'purchase': purchase}), 200


@app.route('/purchases', methods=['GET'])
@add_cors_headers
@token_required
def get_user_purchases(user):  
    purchases = db.query(Purchases).filter_by(buyer_id=user.id).all()
    out = {'purchases': [json.loads(json.dumps(p, cls=AlchemyEncoder)) for p in purchases]}
    return jsonify(out), 200


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


@app.route('/purchases/<purchase_id>', methods=['GET'])
@add_cors_headers
def pay_purchase(purchase_id):  
    trans_id = request.args.get('trans_id')  
    order_id = request.args.get('order_id')  
    amount = request.args.get('amount')  
    
    purchase = db.query(Purchases).filter_by(trans_id=trans_id, id=order_id, price=amount).limit(1).first()
    if purchase is None:
        return (jsonify({'message': 'purchase does not exists.'}), 404)
    
    url = "https://nextpay.org/nx/gateway/verify"
    payload=f'api_key={purchase_api_key}&amount={amount}&trans_id={trans_id}'
    headers = {
        #'User-Agent': 'PostmanRuntime/7.26.8',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status == -90:
        return (jsonify({'message': 'purchase does not completed.'}), 500)

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

    ticket = db.query(Tickets).filter_by(id=data['ticket_id']).limit(1).first()   
    try:
        price = ticket.price
        url = "https://nextpay.org/nx/gateway/token"
        payload='api_key={purchase_api_key}&amount={ticket.price}&order_id={new_purchase.id}&callback_uri={host_url}/purchases/{new_purchase.id}'
        headers = {
            #'User-Agent': 'PostmanRuntime/7.26.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        db.add(new_purchase)  
        db.commit()    
        db.flush()
        return jsonify({'message': 'purchase created successfully', 'purchase_id': new_purchase.id}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'bad parameter type.'}), 400

