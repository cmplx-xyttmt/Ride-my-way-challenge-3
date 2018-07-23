"""
This file contains helper functions to be used in the views.py
It helps keep the codebase manageable
"""
from app.models import User, Ride, Request
from flask import request, abort, jsonify, make_response


def sign_up_user(username, password, email):
    """Signs up a user"""
    user = User.get_user(username)
    if user:
        response = {
            'error': 'Conflict',
            'message': 'User already exists. Choose a different username'
        }
        return make_response(jsonify(response)), 409

    user = User(username=username)
    user.hash_password(password)
    user.email = email
    user_id = user.add_new_user()

    response = {
        'message': 'Signed up successfully',
        'username': user.username,
        'id': user_id,
        'email': email
    }
    return make_response(jsonify(response)), 201
