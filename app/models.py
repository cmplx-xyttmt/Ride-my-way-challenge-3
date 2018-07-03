import psycopg2
from passlib.apps import custom_app_context as pwd_context
from configure_database import config
from app.database_setup import create_tables
import jwt
import datetime
from app import app


class User:

    def __init__(self, username=None, password=None, rides_taken=0, rides_given=0):
        # TODO: Add another field for email address if you have time for implementing notifications
        self.username = username
        self.password_hash = password
        self.rides_taken = rides_taken
        self.rides_given = rides_given
        self.conn = None
        self.cur = None

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def initiate_connection(self):
        """Initiates a connection to the database and sets the cursor"""
        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'

        create_tables()
        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()

    def add_new_user(self):
        """Adds a new user to the database"""
        sql = "INSERT  INTO users (username, user_password, rides_taken, rides_given)" \
              "VALUES (%s, %s, %s, %s) RETURNING user_id"
        user_id = None
        self.initiate_connection()
        try:
            self.cur.execute(sql, (self.username, self.password_hash, self.rides_given, self.rides_taken))
            user_id = self.cur.fetchone()[0]
            self.conn.commit()
            self.cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: ", error)
        finally:
            if self.conn is not None:
                self.conn.close()

        return user_id

    @staticmethod
    def get_user(username):
        """Gets a user from the database whose username matches the one given"""
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
            username = row[1]
            password = row[2]
            rides_taken = row[3]
            rides_given = row[4]
            user = User(username, password, rides_taken, rides_given)
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
        token = jwt.encode(payload, 'string', algorithm='HS256')

        return token
