import unittest
import json
from app.models import User
from app import app


class TestAuth(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.user = User(username='Isaac', password='python')

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
        response = self.client.post("ridemyway/api/v1/auth/login",
                                    content_type="application/json",
                                    data=json.dumps(req_data))

        self.assertEqual(response.status_code, 200)
        data = json.loads(str(response.data.decode()))
        self.assertIn('message', data)
        self.assertIn('access_token', data)
        self.assertEqual(data['message'], "Logged in successfully")


if __name__ == '__main__':
    unittest.main()
