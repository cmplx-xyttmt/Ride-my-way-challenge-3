from app import app
from app.models import User
from flask import request, abort, jsonify, g, make_response
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
rides = []


@app.route('/ridemyway/api/v1/rides', methods=['GET'])
def get_rides():
    rides_as_dicts = [convert_ride_offer(ride) for ride in rides]
    return jsonify({'rides': rides_as_dicts})


def convert_ride_offer(ride_offer):
    """Converts ride offer to json serializable object
    by first converting requests to dict object"""
    ride_requests_list = [ride_req.__dict__
                          for ride_req in ride_offer.requests]
    ride_offer_dict = ride_offer.__dict__
    ride_offer_dict["requests"] = ride_requests_list
    return ride_offer_dict


@app.route('/ridemyway/api/v1/auth/signup', methods=['POST'])
def signup():
    if not request.is_json:
        abort(400, 'Make sure your request contains json data')
    json_request = request.get_json()
    if 'username' not in json_request or 'password' not in json_request:
        abort(400,
              'Make sure you have a name and password attribute in your json request')

    username = json_request['username']
    password = json_request['password']
    if username is None or password is None:
        abort(400, 'Missing arguments')

    user = User.get_user(username)
    if user:
        response = {
            'error': 'Conflict',
            'message': 'User already exists. Choose a different username'
        }
        return make_response(jsonify(response)), 409

    user = User(username=username)
    user.hash_password(password)
    user_id = user.add_new_user()

    response = {
        'message': 'Signed up successfully',
        'username': user.username,
        'id': user_id
    }
    return make_response(jsonify(response)), 201


@app.route('/ridemyway/api/v1/auth/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/ridemyway/api/v1/auth/login', methods=['POST'])
def login():
    """Login an existing user"""
    if not request.is_json:
        abort(400, 'Make sure your request contains json data')

    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    if not username or not password:
        response = {
            'message': 'Make sure you enter a username and a password'
        }
        return make_response(jsonify(response)), 401

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


def verify_password(username, password):
    # try to authenticate with username/password
    user = User.get_user(username=username)
    if not user or not user.verify_password(password):
        return False

    g.user = user
    return True


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": 'Ride Not Found',
                                  "message": error.description}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"error": 'Bad request.',
                                  'message': error.description}), 400)


@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({"error": 'Conflict.',
                                  'message': error.description}))
