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


def login_user(username, password):
    user = User.get_user(username)

    if not user:
        response = {
            'message': 'User account does not exist'
        }
        return make_response(jsonify(response)), 401

    if user.verify_password(password):
        # generate access token
        token = user.generate_auth_token()
        response = {
            'message': 'Logged in successfully',
            'access_token': token.decode('UTF-8')
        }
        return make_response(jsonify(response)), 200

    # If wrong password
    response = {
        'message': 'Invalid user credentials'
    }
    return make_response(jsonify(response)), 401


def return_requests(ride_id, ride, username):
    #  Check if this user is the one that created the ride request
    if ride.name == username:
        requests_list = Request.get_ride_requests(ride_id)
        requests_list = [req.__dict__ for req in requests_list]
        response = {
            'ride_requests': requests_list
        }
        return make_response(jsonify(response)), 200
    else:
        abort(401,
              'You are not authorized to view these '
              'ride requests because you did not create this ride offer.')
