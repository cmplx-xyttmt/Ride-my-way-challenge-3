import psycopg2
from passlib.apps import custom_app_context as pwd_context
from configure_database import config
from app.database_setup import create_tables
import jwt
import datetime
from app.database_helper import Database
from app import app


class User:

    def __init__(self, username=None, password=None,
                 rides_taken=0, rides_given=0):
        self.username = username
        self.user_id = 0  # Default value
        self.password_hash = password
        self.rides_taken = rides_taken
        self.rides_given = rides_given
        self.conn = None
        self.cur = None

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def add_new_user(self):
        """Adds a new user to the database"""
        database_conn = Database()
        columns = ("username",
                   "user_password",
                   "rides_taken",
                   "rides_given")

        values = (self.username,
                  self.password_hash,
                  self.rides_given,
                  self.rides_taken)

        data_returned = database_conn.insert("users",
                                             columns,
                                             values,
                                             "user_id")
        user_id = None
        for row in data_returned:
            user_id = row[0]

        return user_id

    @staticmethod
    def get_user(username):
        """Gets a user from the database
        whose username matches the one given"""
        sql = "SELECT * FROM users WHERE username = (%s)"
        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'
        create_tables()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        user = None
        try:
            cur.execute(sql, (username,))
            row = cur.fetchone()
            if row:
                user_id = row[0]
                username = row[1]
                password = row[2]
                rides_taken = row[3]
                rides_given = row[4]
                user = User(username, password, rides_taken, rides_given)
                user.user_id = user_id
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: ", error)
        finally:
            if conn is not None:
                conn.close()

        return user

    def generate_auth_token(self):
        payload = {
            'user': self.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }
        token = jwt.encode(payload, app.config['SECRET'], algorithm='HS256')

        return token

    @staticmethod
    def decode_token(token):
        """Used to decode a token obtained from the authorization header"""
        try:
            payload = jwt.decode(token,
                                 app.config['SECRET'],
                                 algorithms='HS256')
            return payload['user']
        except jwt.ExpiredSignature:
            return "Token is expired. Please login again"
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login"


class Ride:

    def __init__(self, name, origin, destination, price=0):
        self.id = 0  # Default value
        self.name = name
        self.origin = origin
        self.destination = destination
        self.price = price
        self.requests = []

    def add_new_ride_offer(self, user_id):
        """Adds a new ride offer associated with a specific user"""
        database_conn = Database()
        columns = ("user_id",
                   "origin",
                   "destination",
                   "price")

        values = (user_id,
                  self.origin,
                  self.destination,
                  self.price)

        data_returned = database_conn.insert("rides",
                                             columns,
                                             values,
                                             "ride_id")

        ride_id = None
        for row in data_returned:
            ride_id = row[0]

        self.id = ride_id
        return self.id

    @staticmethod
    def get_one_ride(ride_id):
        """Gets only one ride"""
        sql = "SELECT r.*, u.username FROM rides r " \
              "LEFT JOIN users u ON (u.user_id=r.user_id)" \
              "WHERE r.ride_id = (%s)"

        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'
        create_tables()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        ride = None
        try:
            cur.execute(sql, (ride_id,))
            row = cur.fetchone()
            if row:
                origin = row[2]
                destination = row[3]
                price = row[4]
                username = row[5]
                new_ride = Ride(username, origin, destination, price)
                new_ride.id = row[0]
                ride = new_ride
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return ride

    @staticmethod
    def get_all_rides():
        """Retrieves all the rides from the database"""
        sql = "SELECT r.*, u.username FROM rides r " \
              "LEFT JOIN users u ON (u.user_id=r.user_id)"

        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'
        create_tables()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        rides = []
        try:
            cur.execute(sql)
            row = cur.fetchone()
            while row:
                origin = row[2]
                destination = row[3]
                price = row[4]
                username = row[5]
                new_ride = Ride(username, origin, destination, price)
                new_ride.id = row[0]
                rides.append(new_ride)
                row = cur.fetchone()
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return rides


class Request:

    def __init__(self, name):
        self.id = 0  # Default id value
        self.name = name  # Name of the requester
        self.accepted = False
        self.rejected = False

    def add_ride_request(self, ride_id, passenger_id):
        """Adds a new request into the database"""
        database_conn = Database()
        columns = ("ride_id",
                   "passenger_id",
                   "accepted",
                   "rejected")

        values = (ride_id,
                  passenger_id,
                  self.accepted,
                  self.rejected)

        data_returned = database_conn.insert("riderequests",
                                             columns,
                                             values,
                                             "request_id")

        req_id = None
        for row in data_returned:
            req_id = row[0]

        self.id = req_id
        return self.id

    @staticmethod
    def get_ride_requests(ride_id):
        """Gets all the ride requests for a particular ride offer"""
        sql = "SELECT r.*, u.username FROM riderequests r " \
              "LEFT JOIN users u on r.passenger_id = u.user_id" \
              " WHERE r.ride_id = (%s)"

        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'
        create_tables()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        ride_requests = []
        try:
            cur.execute(sql, (ride_id, ))
            row = cur.fetchone()
            while row:
                rq_id = row[0]
                rq_acc = row[3]
                rq_rej = row[4]
                rq_name = row[5]
                ride_req = Request(rq_name)
                ride_req.id = rq_id
                ride_req.accepted = rq_acc
                ride_req.rejected = rq_rej
                ride_requests.append(ride_req)
                row = cur.fetchone()

            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return ride_requests

    @staticmethod
    def accept_reject_ride_request(decision, request_id):
        """Method to accept/reject a ride request"""
        sql = "UPDATE riderequests SET " \
              "accepted = (%s), rejected = (%s)" \
              "WHERE riderequests.request_id = (%s)"

        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'
        create_tables()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        status = False
        try:
            if decision == 'accept':
                accepted = True
                rejected = False
            else:
                accepted = False
                rejected = True

            cur.execute(sql, (accepted, rejected, request_id))
            conn.commit()
            cur.close()
            status = True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return status
