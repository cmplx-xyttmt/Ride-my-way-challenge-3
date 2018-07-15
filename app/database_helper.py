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

        return_val = self.execute_sql(sql)
        return return_val

    def select(self, table, columns, left_join=None, where=None):
        """
        Selects elements in the database using the select statement
        """
        columns = str(columns).replace("\'", "")
        sql = "SELECT " + columns + " FROM " + table
        if left_join:
            sql = sql + " LEFT JOIN " + left_join
        if where:
            sql = sql + " WHERE " + where

        return_val = self.execute_sql(sql)
        return return_val

    def update(self, table, sett, where=None):
        sql = "UPDATE " + table + " SET " + sett
        if where:
            sql = sql + " WHERE " + where

        return_val = self.execute_sql(sql, fetch=False)
        return return_val

    def execute_sql(self, sql, fetch=True):
        """Executes the sql statement and returns the values from the database"""
        return_val = None
        try:
            self.cur.execute(sql)
            if fetch:
                return_val = self.cur.fetchall()
            self.conn.commit()
            self.cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: ", error)
        finally:
            if self.conn is not None:
                self.conn.close()

        return return_val
