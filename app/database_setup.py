import psycopg2
from configure_database import config
from app import app
import os


def create_tables():
    """Creates the necessary tables in the database if they do not exist"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
          user_id SERIAL PRIMARY KEY,
          username VARCHAR(255) NOT NULL,
          user_password VARCHAR(255) NOT NULL,
          rides_taken INTEGER,
          rides_given INTEGER,
          email TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS rides (
          ride_id SERIAL PRIMARY KEY ,
          user_id INTEGER NOT NULL,
          FOREIGN KEY (user_id)
          REFERENCES users(user_id)
          ON UPDATE CASCADE ON DELETE CASCADE,
          origin VARCHAR(255) NOT NULL,
          destination VARCHAR(255) NOT NULL,
          price INTEGER NOT NULL 
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS riderequests (
          request_id SERIAL PRIMARY KEY,
          ride_id INTEGER NOT NULL,
          passenger_id INTEGER NOT NULL,
          FOREIGN KEY (ride_id)
          REFERENCES rides(ride_id)
          ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (passenger_id)
          REFERENCES users(user_id)
          ON UPDATE CASCADE ON DELETE CASCADE, 
          accepted BOOLEAN,
          rejected BOOLEAN
        )
        """
    )

    conn = None
    try:
        # Read the connection parameters
        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'

        if 'DATABASE_URL' in os.environ:
            database_url = os.environ['DATABASE_URL']
            print(database_url)
            conn = psycopg2.connect(database_url,
                                    sslmode='require')
        else:
            conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # create the tables one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
