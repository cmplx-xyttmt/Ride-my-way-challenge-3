import psycopg2
from configure_database import config
from app.database_setup import create_tables
from app import app


class Database:
    """This class contains helper methods for connecting to the database"""

    def __init__(self):
        """Initiates connection to the database"""
        params = config()
        if app.config['TESTING']:
            params['database'] = 'ridemywaydb_testing'

        create_tables()
        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()

    def insert(self, table, columns, values, returning=None):
        """
        Inserts elements into a table given columns and values
        Returns the values returned after executing the sql statement
        """
        columns = str(columns).replace("\'", "")
        values = str(values)
        sql = "INSERT INTO " + table + " " + columns + " VALUES " + values
        if returning:
            sql = sql + " RETURNING " + returning

        return_val = None
        try:
            self.cur.execute(sql)
            return_val = self.cur.fetchall()
            self.conn.commit()
            self.cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: ", error)
        finally:
            if self.conn is not None:
                self.conn.close()

        return return_val
