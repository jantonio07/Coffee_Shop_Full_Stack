import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

NO_DRINKS_TO_SHOW_MESSAGE = "No drinks to show"
NO_DRINK_FOUND_MESSAGE = "No drink found"
PROPERTY_TO_CHANGE_INVALID_MESSAGE = "Property to change invalid"

app = Flask(__name__)
setup_db(app)
CORS(app)

with app.app_context():
    db_drop_and_create_all()


# ROUTES
@app.route('/drinks')
def get_drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        if len(drinks) == 0:
            raise Exception(NO_DRINKS_TO_SHOW_MESSAGE)
        return jsonify({
                "success": True,
                "drinks": drinks,
            })
    except Exception as e:
        if e.__str__() == NO_DRINKS_TO_SHOW_MESSAGE:
            abort(404)
        else:
            abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        if len(drinks) == 0:
            raise Exception(NO_DRINKS_TO_SHOW_MESSAGE)
        return jsonify({
                "success": True,
                "drinks": drinks,
            })
    except Exception as e:
        if e.__str__() == NO_DRINKS_TO_SHOW_MESSAGE:
            abort(404)
        else:
            abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    data = request.get_json()
    try:
        drink = Drink(
            title=data["title"],
            recipe=str(data["recipe"]).replace("\'", "\""),
        )
        drink.insert()
        return jsonify({
                "success": True,
                "drinks": [drink.long()]
            })
    except Exception as _:
        abort(422)


@app.route('/drinks/<int:drinkId>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drinkId):
    try:
        drink = Drink.query.filter_by(id=drinkId).first()
        if drink is None:
            raise Exception(NO_DRINK_FOUND_MESSAGE)
        data = request.get_json()
        for attr in data:
            if attr == "id":
                pass
            elif attr == "title":
                drink.title = data[attr]
            elif attr == "recipe":
                drink.recipe = str(data[attr]).replace("\'", "\"")
            else:
                raise Exception(PROPERTY_TO_CHANGE_INVALID_MESSAGE)
        drink.update()
        return jsonify({
                    "success": True,
                    "drinks": [drink.long()]
               })
    except Exception as e:
        if e.__str__() == NO_DRINK_FOUND_MESSAGE:
            abort(404)
        elif e.__str__() == PROPERTY_TO_CHANGE_INVALID_MESSAGE:
            abort(400)
        else:
            abort(422)


@app.route('/drinks/<int:drinkId>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_question(payload, drinkId):
    try:
        drink = Drink.query.filter_by(id=drinkId).first()
        if drink is None:
            raise Exception(NO_DRINK_FOUND_MESSAGE)
        drink.delete()
        return jsonify({
                    "success": True,
                    "delete": drinkId
               })
    except Exception as e:
        if e.__str__() == NO_DRINK_FOUND_MESSAGE:
            abort(404)
        else:
            abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                }
            ), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                }
            ), 400


@app.errorhandler(405)
def not_found(error):
    return jsonify(
                {
                    "success": False,
                    "error": 405,
                    "message": "method not allowed"
                }
            ), 405


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify(
                {
                    "success": False,
                    "error": error.status_code,
                    "message": error.error,
                }
            ), error.status_code
