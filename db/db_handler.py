from datetime import datetime
from datetime import timedelta
import sqlite3
from sqlite3 import Error
from db.models.user_luck import UserLuck
from db.models.cowboy_react import CowboyReact
from typing import List

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

    def __create_feature_requests_table(self):
        sql_create_feature_requests_table = ''' CREATE TABLE IF NOT EXISTS FeatureRequests (
                                                    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                    Feature VARCHAR(250)
                                                );'''
        cursor = self.__conn.cursor()
        cursor.execute(sql_create_feature_requests_table)

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
        sql_create_luck_table = ''' CREATE TABLE IF NOT EXISTS UserIdLuck (
                                                    UserId INTEGER PRIMARY KEY NOT NULL,
                                                    Username TEXT NOT NULL,
                                                    LuckyCount INT NOT NULL DEFAULT 0,
                                                    UnluckyCount INT NOT NULL DEFAULT 0,
                                                    LastRoll TEXT DEFAULT CURRENT_TIMESTAMP,
                                                    CurrentLuckyStreak INTEGER NOT NULL DEFAULT 0,
                                                    CurrentUnluckyStreak INTEGER NOT NULL DEFAULT 0
                                                );'''
        cursor = self.__conn.cursor()
        cursor.execute(sql_create_luck_table)

        return
    
    def get_user_luck(self,user_id) -> UserLuck:
        sql = '''
                SELECT 
                    UserId,
                    Username,
                    LuckyCount,
                    UnluckyCount,
                    LastRoll,
                    CurrentLuckyStreak,
                    CurrentUnluckyStreak
                FROM UserIdLuck
                WHERE UserId=?
              '''
        rows = []
        cursor = self.__conn.cursor()
        try:
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
        except Error as e:
            print(e)

        if (len(rows) > 0):
            row = rows[0]
            user_row = UserLuck(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            return user_row
        else:
            return None
    
    def get_user_luck_all(self) -> List[UserLuck]: 
        sql = '''
                SELECT 
                    UserId,
                    Username,
                    LuckyCount,
                    UnluckyCount,
                    LastRoll,
                    CurrentLuckyStreak,
                    CurrentUnluckyStreak
                FROM UserIdLuck
              '''
        rows = []
        results = []

        try:
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                results.append(UserLuck(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
        except Error as e:
            print(e)

        return results
    
    def initialize_user_luck_row(self,user_id,username):
        try:
            with self.__conn:
                now = datetime.now()
                datetime_string = now.strftime("%m/%d/%Y")
                sql = ''' INSERT INTO UserIdLuck VALUES(?,?,?,?,?,?,?) '''
                try:
                    cursor = self.__conn.cursor()
                    cursor.execute(sql, (user_id,username,0,0,datetime_string,0,0))
                except Error as e:
                    print(e)
                return
        except Error as e:
            print(e)

    def update_user_luck_row(self,user_luck: UserLuck):
        now = datetime.now()
        datetime_string = now.strftime("%m/%d/%Y")
        try:
            with self.__conn:
                sql = '''
                        UPDATE UserIdLuck
                        SET LuckyCount = ? ,
                            UnluckyCount = ? ,
                            LastRoll = ? ,
                            Username = ? ,
                            CurrentLuckyStreak = ?,
                            CurrentUnluckyStreak = ? 
                        WHERE UserId = ?
                        '''
                cursor = self.__conn.cursor()
                cursor.execute(sql, (user_luck.lucky, user_luck.unlucky, datetime_string, user_luck.user, user_luck.currentLuckyStreak, user_luck.currentUnluckyStreak, user_luck.user_id))
        except Error as e:
            print(e)
                               