import sqlite3
from sqlite3 import Error

class DbHandler():
    def __init__(self):
        self.__db_location = r"C:\sqlite\cowboybot\pythonsqlite.db"
        self.__conn = self.__create_connection(self.__db_location)
        self.__create_howdy_reacts_table()

    def __create_connection(self,db_file):
        try:
            conn = sqlite3.connect(db_file)
            print("connected to db")
            return conn
        except Error as e:
            print(e)

    def __create_howdy_reacts_table(self):
        sql_create_howdy_reacts_table = ''' CREATE TABLE CowboyReacts (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                triggerWord TEXT NOT NULL
                                            );'''
        try:
            cursor = self.__conn.cursor()
            cursor.execute(sql_create_howdy_reacts_table)
        except Error as e:
            print(e)

        return

    def insert_cowboy_reacts_table(self,triggerWord):
        with self.__conn:
            print('inserting: ' + triggerWord)
            sql = ''' INSERT INTO CowboyReacts VALUES(?, ?) '''
            cursor = self.__conn.cursor()
            cursor.execute(sql, (None,triggerWord))
            last_row_id = cursor.lastrowid

            return last_row_id

    def get_cowboy_reacts(self):
        cursor = self.__conn.cursor()
        cursor.execute("SELECT triggerWord FROM CowboyReacts")
        rows = cursor.fetchall()
        return rows
