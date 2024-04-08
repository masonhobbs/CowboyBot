import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db.tables.base_db_class import BaseDbClass

class DbHandler():
    def __init__(self):
        db_url = r"sqlite:///cowboy_db.db"
        self.__db_location = r"cowboy_db.db"
        self.__conn = self.__create_connection(self.__db_location)

        self.engine = create_engine(db_url, echo=False)
        BaseDbClass.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.__create_howdy_reacts_table()

    def __create_connection(self,db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
            
    def __create_howdy_reacts_table(self):
        sql_create_howdy_reacts_table = ''' CREATE TABLE IF NOT EXISTS CowboyReacts (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                triggerWord TEXT NOT NULL
                                            );'''
        cursor = self.__conn.cursor()
        cursor.execute(sql_create_howdy_reacts_table)

        return

    def insert_cowboy_reacts_table(self,triggerWord):
        with self.__conn:
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
    
    def get_cowboy_reacts_count(self):
        cursor = self.__conn.cursor()
        cursor.execute("SELECT triggerWord, COUNT(*) FROM CowboyReacts GROUP BY triggerWord")
        rows = cursor.fetchall()
        return rows