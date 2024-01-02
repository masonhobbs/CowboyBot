from typing import Any, Type, Union, TypeVar, Generic
import discord
from discord.app_commands import tree
import datetime
import sqlalchemy
from db.db_handler import DbHandler
from db.tables.roll_streak_record import RollStreakRecord
T = TypeVar('T')

class BaseRollHelper():
    def __init__(self, user: Union[discord.User, discord.Member], db: DbHandler, table: T):
        self.user = user
        self.db = db
        self.user_name: str = ""
        self.table_type = table
    
        if hasattr(self.user, "nick") and self.user.nick is not None and len(self.user.nick) > 0:
            self.user_name = self.user.nick
        elif hasattr(self.user, "global_name") and self.user.global_name is not None and len(self.user.global_name) > 0:
            self.user_name = self.user.global_name
        elif hasattr(self.user, "display_name") and self.user.display_name is not None and len(self.user.display_name) > 0:
            self.user_name = self.user.display_name
        else:
            self.user_name = self.user.name

        self.user_row = self.get_user_row()
        if self.user_row is None:
            new_row = self.build_new_user_row()
            self.insert_new_user_row(new_row)
            self.user_row = self.get_user_row()
        
    def get_user_row(self) -> T:
        return self.db.session.scalars(sqlalchemy.select(self.table_type).where(self.table_type.UserId == self.user.id)).one_or_none()
    
    def get_current_streak_records(self) -> RollStreakRecord:
        return self.db.session.scalars(sqlalchemy.select(RollStreakRecord)).first()

    def process_roll(self, is_lucky: bool, today_date_str: str):
        has_rolled = self.has_already_rolled(today_date_str)
        if has_rolled is False:
            if is_lucky is True:
                self.user_row.LuckyCount += 1
                self.user_row.CurrentLuckyStreak += 1
                self.user_row.CurrentUnluckyStreak = 0
            else:
                self.user_row.UnluckyCount += 1
                self.user_row.CurrentLuckyStreak = 0
                self.user_row.CurrentUnluckyStreak += 1
            self.user_row.LastRoll = today_date_str
            self.user_row.Username = self.user_name

        streak_record = self.get_current_streak_records()
        if self.user_row.CurrentLuckyStreak > streak_record.HighestLuckyStreak:
            streak_record.HighestLuckyStreak = self.user_row.CurrentLuckyStreak
        if self.user_row.CurrentUnluckyStreak > streak_record.HighestUnluckyStreak:
            streak_record.HighestUnluckyStreak = self.user_row.CurrentUnluckyStreak
        
        self.save_changes()
        return self.user_row

    def has_already_rolled(self,today_date_string: str): 
        if self.user_row.LastRoll == today_date_string:
            return True
    
        return False
    
    def generate_result_message(self, lucky_emoji: str, unlucky_emoji: str, header: str):
        msg = "\n\n"
        if header is not None:
            msg = "\n\n" + header + " Stats:\n"
        msg = msg + lucky_emoji + ' `' + str(self.user_row.LuckyCount) + "`\u200B \u200B \u200B \u200B " + unlucky_emoji + '`' + str(self.user_row.UnluckyCount) + "`"
        return msg
    
    def build_new_user_row(self) -> T:
        new_row = self.table_type(
            UserId=self.user.id, 
            Username=self.user_name,
            LuckyCount=0,
            UnluckyCount=0,
            LastRoll="",
            CurrentLuckyStreak=0,
            CurrentUnluckyStreak=0)
        return new_row
    
    def insert_new_user_row(self, new_row: T):
        self.db.session.add(new_row)
        self.save_changes()

    def save_changes(self):
        self.db.session.commit()

