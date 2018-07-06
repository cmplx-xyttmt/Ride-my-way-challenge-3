import unittest
import psycopg2
from configure_database import config
import json
from app.models import User, Ride
from app import app


class TestAuth(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.user = User(username='Isaac', password='python')
        self.user2 = User(username='Owomugisha', password='java')
        self.token = self.login_signup(self.user2)
        self.user3 = User(username='Allen', password='cplusplus')
        self.ride_1 = Ride("Isaac", "Ibanda", "Kampala")

    def sign_up_user(self, user):
        """Helper method that issues the request to sign up a user"""
        req_data = {'username': user.username,
                    'password': user.password_hash}
        response = self.client.post("ridemyway/api/v1/auth/signup",
                                    content_type="application/json",
                                    data=json.dumps(req_data))
        return response

    def login_user(self, user):
        """Helper method that issues the request to login a user"""
        req_data = {'username': user.username,
                    'password': user.password_hash}
        response = self.client.post("ridemyway/api/v1/auth/login",
                                    content_type="application/json",
                                    data=json.dumps(req_data))
        return response

    def login_signup(self, user):
        """Helper method to login and sign up a user"""
        resp = self.sign_up_user(user)
        self.assertEqual(201, resp.status_code)
        resp = self.login_user(user)
        self.assertEqual(200, resp.status_code)
        data = json.loads(str(resp.data.decode()))
        self.assertIn('access_token', data)

        return data['access_token']

    def create_ride(self, ride, token):
        """Helper method that issues the request to create a new ride offer"""
        req_data = {'name': ride.name,
                    'origin': ride.origin,
                    'destination': ride.destination,
                    'price': ride.price}
        response = self.client.post("/ridemyway/api/v1/users/rides",
                                    content_type="application/json",
                                    data=json.dumps(req_data),
                                    headers={'Authorization': token})
        return response

    def create_request(self, token):
        """Helper method for creating ride requests"""
        resp = self.client.post("/ridemyway/api/v1/rides/{}/requests".
                                format(1),
                                headers={'Authorization': token})
        return resp

    def test_signup(self):
        """Tests whether a new user can sign up"""
        response = self.sign_up_user(self.user)

        self.assertEqual(response.status_code, 201)
        data = json.loads(str(response.data.decode()))
        self.assertEqual(data['username'], self.user.username)

    def test_login(self):
        """Tests if a user can login"""

        # First sign up the user
        self.sign_up_user(self.user)
        response = self.login_user(self.user)

        self.assertEqual(response.status_code, 200)
        data = json.loads(str(response.data.decode()))
        self.assertIn('message', data)
        self.assertIn('access_token', data)
        self.assertEqual(data['message'], "Logged in successfully")

    def test_rides_with_token(self):
        """Tests whether a user can view rides when logged in"""
        token = self.token
        resp = self.create_ride(self.ride_1, token)
        self.assertEqual(201, resp.status_code)
        resp = self.client.get("/ridemyway/api/v1/rides",
                               headers={'Authorization': token})
        data = json.loads(str(resp.data.decode()))
        self.assertEqual(200, resp.status_code)
        self.assertIn("rides", data)

    def test_rides_no_auth_token(self):
        """Tests whether a user can view rides without being logged in."""
        response = self.client.get("/ridemyway/api/v1/rides")
        self.assertEqual(401, response.status_code)
        data = json.loads(str(response.data.decode()))
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Please provide an access token')

    def test_rides_with_wrong_auth(self):
        """Tests whether a user can view rides with a wrong auth token"""
        # Add some characters to make the token invalid
        token = self.token + "isaac"
        resp = self.client.get("/ridemyway/api/v1/rides",
                               headers={'Authorization': token})

        data = json.loads(str(resp.data.decode()))
        self.assertEqual(401, resp.status_code)
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'],
                         'Invalid token. Please register or login')

    def test_get_one_ride(self):
        """Tests whether a user can view one ride"""
        token = self.token

        resp = self.create_ride(self.ride_1, token)
        self.assertEqual(201, resp.status_code)
        resp = self.client.get("/ridemyway/api/v1/rides/{}".
                               format(1),
                               headers={'Authorization': token})
        self.assertEqual(200, resp.status_code)
        data = json.loads(str(resp.data.decode()))
        self.assertIn('ride', data)

    def test_create_ride_request(self):
        """Tests whether a user can create a ride request"""
        token = self.token

        resp = self.create_ride(self.ride_1, token)
        self.assertEqual(201, resp.status_code)
        resp = self.client.post("/ridemyway/api/v1/rides/{}/requests".
                                format(1),
                                headers={'Authorization': token})
        self.assertEqual(201, resp.status_code)
        data = json.loads(str(resp.data.decode()))
        self.assertIn('message', data)
        self.assertIn('request_id', data)
        self.assertIn('ride_request', data)

    def test_view_ride_requests(self):
        """Tests whether a user that created a ride request can view the ride requests"""
        token = self.token

        resp = self.create_ride(self.ride_1, token)
        self.assertEqual(201, resp.status_code)
        resp = self.create_request(token)
        self.assertEqual(201, resp.status_code)
        resp = self.client.get("/ridemyway/api/v1/users/rides/{}/requests".
                               format(1),
                               headers={'Authorization': token})
        self.assertEqual(200, resp.status_code)
        data = json.loads(str(resp.data.decode()))
        self.assertIn('ride_requests', data)

    def tearDown(self):
        """Deletes the tables in the database after using it for testing"""
        sql = "DROP SCHEMA public CASCADE"
        sql2 = "CREATE SCHEMA public"
        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'

        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        try:
            cur.execute(sql)
            cur.execute(sql2)
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: ", error)
        finally:
            if conn is not None:
                conn.close()


if __name__ == '__main__':
    unittest.main()
