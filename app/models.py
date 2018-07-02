import psycopg2
from passlib.apps import custom_app_context as pwd_context
from app.database_setup import config


class User:

    def __init__(self, username=None, password=None):
        self.username = username
        self.password_hash = password
        self.rides_taken = 0
        self.rides_given = 0
        self.conn = None
        self.cur = None

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def initiate_connection(self):
        """Initiates a connection to the database and sets the cursor"""
        params = config()
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
