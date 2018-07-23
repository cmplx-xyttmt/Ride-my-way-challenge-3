from app import app
from app.models import User, Ride, Request
from flask import request, abort, jsonify, make_response
from app.helper_functions import sign_up_user, \
    login_user, return_requests, accept_or_reject
from app.validators import Validate


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
              'Make sure you have a name '
              'and password attribute in your json request')

    username = json_request['username']
    password = json_request['password']
    email = json_request['email']
    if username is None or \
            password is None or \
            email is None:
        abort(400, 'Missing arguments')

    val = Validate.validate_username(username)
    if not val[0]:
        abort(401, val[1])
    val = Validate.validate_password(password)
    if not val[0]:
        abort(401, val[1])
    val = Validate.validate_email(email)
    if not val[0]:
        abort(401, val[1])

    return sign_up_user(username, password, email)


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

    val = Validate.validate_username(username)
    if not val[0]:
        abort(401, val[1])
    val = Validate.validate_password(password)
    if not val[0]:
        abort(401, val[1])

    return login_user(username, password)


@app.route('/ridemyway/api/v1/rides', methods=['GET'])
def get_rides():
    """API endpoint for getting all the ride offers"""

    access_token = request.headers.get('Authorization')
    if access_token:
        verify_token(access_token)
        ride_offers = Ride.get_all_rides()
        rides_as_dicts = [convert_ride_offer(ride) for ride in ride_offers]
        return jsonify({'rides': rides_as_dicts}), 200
    else:
        abort(401, 'Please provide an access token')


@app.route('/ridemyway/api/v1/user/rides', methods=['GET'])
def get_my_rides():
    """API endpoint for getting a particular users rides"""
    access_token = request.headers.get('Authorization')
    if access_token:
        username = verify_token(access_token)

        ride_offers = Ride.get_all_rides(username)
        rides_as_dicts = [convert_ride_offer(ride) for ride in ride_offers]
        return jsonify({'rides': rides_as_dicts}), 200
    else:
        abort(401, 'Please provide an access token')


@app.route('/ridemyway/api/v1/rides/<ride_id>')
def get_ride(ride_id):
    """API endpoint to retrieve a single ride"""
    try:
        ride_id = int(ride_id)
    except ValueError:
        ride_id = ride_id

    if type(ride_id) is not int:
        abort(400, 'Make sure the ride id is an integer')

    access_token = request.headers.get('Authorization')
    if access_token:
        verify_token(access_token)
        ride = Ride.get_one_ride(ride_id)
        if ride:
            return jsonify({'ride': convert_ride_offer(ride)}), 200
        else:
            abort(400, 'Ride does not exist.')
    else:
        abort(401, 'Please provide an access token')


@app.route('/ridemyway/api/v1/users/rides', methods=['POST'])
def create_ride():
    """Endpoint for creating a new ride offer"""
    if not request.is_json:
        abort(400, 'Make sure your request contains json data')

    access_token = request.headers.get('Authorization')
    if access_token:
        username = verify_token(access_token)

        if not request.is_json:
            abort(400, 'Make sure your request contains json data')

        data = request.get_json()
        if 'origin' not in data or \
                'destination' not in data:
            abort(400,
                  'Make sure you have specified name, '
                  'origin and destination attributes in your json request.')

        ride_offer = Ride(username,
                          data['origin'],
                          data['destination'],
                          data.get('price', 0))

        print(username)
        user = User.get_user(username)
        ride_id = ride_offer.add_new_ride_offer(user.user_id)
        response = {
            'message': 'Ride created successfully',
            'ride_id': ride_id,
            'ride': convert_ride_offer(ride_offer)
        }

        return make_response(jsonify(response)), 201
    else:
        abort(401, 'Please provide an access token')


@app.route('/ridemyway/api/v1/rides/<ride_id>/requests', methods=['POST'])
def create_ride_request(ride_id):
    try:
        ride_id = int(ride_id)
    except ValueError:
        ride_id = ride_id

    if type(ride_id) is not int:
        abort(400, 'Make sure the ride id is an integer')

    access_token = request.headers.get('Authorization')
    if access_token:
        username = verify_token(access_token)
        requester = User.get_user(username)
        ride_req = Request(username)
        req_id = ride_req.add_ride_request(ride_id, requester.user_id)
        response = {
            'message': 'Ride request created successfully',
            'request_id': req_id,
            'ride_request': ride_req.__dict__
        }
        return make_response(jsonify(response)), 201
    else:
        abort(401, 'Please provide an access token')


@app.route('/ridemyway/api/v1/users/rides/<ride_id>/requests', methods=['GET'])
def view_ride_requests(ride_id):
    if not Validate.validate_int(ride_id):
        abort(400, 'Make sure the ride id is an integer')

    access_token = request.headers.get('Authorization')
    if access_token:
        username = verify_token(access_token)
        ride = Ride.get_one_ride(ride_id)
        if not ride:
            abort(400, 'Ride does not exist.')

        return return_requests(ride_id, ride, username)
    else:
        abort(401, 'Please provide an access token')


@app.route('/ridemyway/api/v1/users/rides/<ride_id>/requests/<request_id>',
           methods=['PUT'])
def accept_reject_request(ride_id, request_id):
    if not Validate.validate_int(ride_id) or \
            not Validate.validate_int(request_id):
        abort(400, 'Make sure the ride and request ids are integers')

    access_token = request.headers.get('Authorization')
    if access_token:
        username = verify_token(access_token)
        ride = Ride.get_one_ride(ride_id)

        #  Check if this user is the one that created the ride request
        if ride.name == username:
            if not request.is_json:
                abort(400, 'Make sure your request contains json data')

            data = request.get_json()
            return accept_or_reject(request_id, data)
        else:
            abort(401,
                  'You are not authorized to respond to this '
                  'ride request because you did not create this ride offer.')

    else:
        abort(401, 'Please provide an access token')


def verify_token(access_token):
    """Determine if the access token is correct"""
    username = User.decode_token(access_token)

    if username == "Invalid token. Please register or login":
        abort(401, username)
    elif username == "Token is expired. Please login again":
        abort(401, username)
    return username


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": 'Resource Not Found',
                                  "message": error.description}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"error": 'Bad request.',
                                  'message': error.description}), 400)


@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({"error": 'Conflict.',
                                  'message': error.description}), 409)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({"error": 'Unauthorized access.',
                                  'message': error.description}), 401)


@app.errorhandler(405)
def method_not_allowed(error):
    message = "{} Check the documentation for allowed methods".\
        format(error.description)
    return make_response(jsonify({"error": 'Method not allowed',
                                  "message": message}), 405)
