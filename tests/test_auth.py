import unittest
import psycopg2
from configure_database import config
import json
from app.models import User
from app import app


class TestAuth(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.user = User(username='Isaac', password='python')
        self.user2 = User(username='Owomugisha', password='java')
        self.user3 = User(username='Allen', password='cplusplus')
        self.ride_1 = {}

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

    def test_signup(self):
        """Tests whether a new user can sign up"""
        req_data = {'username': self.user.username,
                    'password': "python"}
        response = self.client.post("ridemyway/api/v1/auth/signup",
                                    content_type="application/json",
                                    data=json.dumps(req_data))

        self.assertEqual(response.status_code, 201)
        data = json.loads(str(response.data.decode()))
        self.assertEqual(data['username'], self.user.username)

    def test_login(self):
        """Tests if a user can login"""
        req_data = {'username': self.user.username,
                    'password': "python"}

        # First sign up the user
        self.client.post("ridemyway/api/v1/auth/signup",
                         content_type="application/json",
                         data=json.dumps(req_data))

        response = self.client.post("ridemyway/api/v1/auth/login",
                                    content_type="application/json",
                                    data=json.dumps(req_data))

        self.assertEqual(response.status_code, 200)
        data = json.loads(str(response.data.decode()))
        self.assertIn('message', data)
        self.assertIn('access_token', data)
        self.assertEqual(data['message'], "Logged in successfully")

    def test_rides_no_auth_token(self):
        """Tests whether a user can access rides without being logged in."""
        response = self.client.get("/ridemyway/api/v1/rides")
        self.assertEqual(401, response.status_code)
        data = json.loads(str(response.data.decode()))
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Please provide an access token')

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
