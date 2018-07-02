from app import app
from app.models import User
from flask import request, abort, jsonify

rides = []


@app.route('/ridemyway/api/v1/rides', methods=['GET'])
def get_ride():
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
    # TODO: Add a check for existing user
    user = User(username=username)
    user.hash_password(password)
    user_id = user.add_new_user()
    print(user_id)
    return jsonify({'username': user.username}), 201
