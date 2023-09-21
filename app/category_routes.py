from flask import request, jsonify, Blueprint
from . import db
from .models import Categories
from .helper import token_required, add_cors_headers


app = Blueprint('category_routes_blueprint', __name__)


def validate_category_data(data):
    if not 'name' in data:
        return (jsonify({'message': 'category must have "name".'}), 400)
    category = db.query(Categories).filter_by(name=data['name']).limit(1).first()   
    if category is not None:
        return (jsonify({'message': 'category already exists.'}), 400)
    return None


def authorize_categpry(user, category_name):
    category = db.query(Caterogies).filter_by(name=category_name).limit(1).first()
    if category is None:
        return (jsonify({'message': 'category does not exists.'}), 404)
    if not user.is_admin:
        return (jsonify({'message': 'you are not admin to edit or delete a category.'}), 403)
    return None


@app.route('/categories', methods=['GET'])
@add_cors_headers
def get_categories():  
    categories = db.query(Categories).all()
    return jsonify([category.name for category in categories]), 200


@app.route('/categories/<category_name>', methods=['DELETE'])
@add_cors_headers
@token_required
def delete_category(user, category_name):  
    err = authorize_category(user, category_name)
    if err is not None:
        return err

    category = db.query(Categories).filter_by(name=category_name).limit(1).first()
    try:
        db.delete(category)  
        db.commit()    
        return jsonify({'message': 'category deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'somthing went wrong.'}), 500


@app.route('/categories/<category_name>', methods=['PUT'])
@add_cors_headers
@token_required
def edit_category(user, category_name):  
    data = request.get_json()  
    err = validate_category_data(data) 
    if err is not None:
        return err

    err = authorize_category(user, category_name)
    if err is not None:
        return err

    try:
        category.name = data['name']
        db.commit()    
        db.flush()
        return jsonify({'message': 'category updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'something went wrong.'}), 500


@app.route('/categories', methods=['POST'])
@add_cors_headers
@token_required
def create_category(user):  
    data = request.get_json()
    err = validate_category_data(data) 
    if err is not None:
        return err
    try:
        new_category = Categories(**data) 
        db.add(new_category)  
        db.commit()    
        db.flush()
        return jsonify({'message': 'category created successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'bad parameter type.'}), 400

