from datetime import datetime
import sqlite3
from sqlite3 import Error

class DbHandler():
    def __init__(self):
        self.__db_location = r"C:\Users\mhobb\Documents\CowboyBot\sqlite\cowboybot\pythonsqllite.db"
        self.__conn = self.__create_connection(self.__db_location)
        self.__create_howdy_reacts_table()
        self.__create_feature_requests_table()
        self.__create_luck_table()

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

    def __create_feature_requests_table(self):
        sql_create_feature_requests_table = ''' CREATE TABLE FeatureRequests (
                                                    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                    Feature VARCHAR(250)
                                                );'''
        try:
            cursor = self.__conn.cursor()
            cursor.execute(sql_create_feature_requests_table)
        except Error as e:
            print(e)

        return          

    def insert_feature_requests_table(self,feature):
        with self.__conn:
            sql = ''' INSERT INTO FeatureRequests VALUES(?,?) '''
            cursor = self.__conn.cursor()
            cursor.execute(sql, (None,feature))
            last_row_id = cursor.lastrowid

            return last_row_id

    def get_feature_requests(self):
        cursor = self.__conn.cursor()
        cursor.execute("SELECT Id, Feature FROM FeatureRequests")
        rows = cursor.fetchall()
        return rows

    def delete_feature_request(self,feature):
        sql = ''' DELETE FROM FeatureRequests WHERE Feature LIKE ? '''
        cursor = self.__conn.cursor()
        
        try:
            cursor.execute(sql, ('%'+str(feature)+'%',))
        except Error as e:
            print(e)

        return

    def __create_luck_table(self):
        sql_create_luck_table = ''' CREATE TABLE UserLuck (
                                                    Username TEXT PRIMARY KEY NOT NULL,
                                                    LuckyCount INT NOT NULL DEFAULT 0,
                                                    UnluckyCount INT NOT NULL DEFAULT 0,
                                                    LastRoll TEXT DEFAULT CURRENT_TIMESTAMP
                                                );'''
        try:
            cursor = self.__conn.cursor()
            cursor.execute(sql_create_luck_table)
        except Error as e:
            print(e)

        return
    
    def get_user_luck(self,username):
        sql = '''
                SELECT Username, LuckyCount, UnluckyCount, LastRoll
                FROM UserLuck
                WHERE Username=?
              '''
        rows = []
        cursor = self.__conn.cursor()
        try:
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
        except Error as e:
            print(e)

        return rows
    
    def get_user_luck_all(self):
        sql = '''
                SELECT Username, LuckyCount, UnluckyCount, LastRoll
                FROM UserLuck
              '''
        rows = []
        try:
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
        except Error as e:
            print(e)

        return rows
    
    def initialize_user_luck_row(self,username,luckyCount,unluckyCount):
        try:
            with self.__conn:
                now = datetime.now()
                datetime_string = now.strftime("%m/%d/%Y")
                sql = ''' INSERT INTO UserLuck VALUES(?,?,?,?) '''
                try:
                    cursor = self.__conn.cursor()
                    cursor.execute(sql, (username,luckyCount,unluckyCount,datetime_string))
                except Error as e:
                    print(e)
                return
        except Error as e:
            print(e)

    def update_user_luck_row(self,username,luckyCount,unluckyCount):
        now = datetime.now()
        datetime_string = now.strftime("%m/%d/%Y")
        try:
            with self.__conn:
                sql = '''
                        UPDATE UserLuck
                        SET LuckyCount = ? ,
                            UnluckyCount = ? ,
                            LastRoll = ?
                        WHERE Username = ?
                        '''
                cursor = self.__conn.cursor()
                cursor.execute(sql, (luckyCount, unluckyCount, datetime_string, username))
        except Error as e:
            print(e)
                               