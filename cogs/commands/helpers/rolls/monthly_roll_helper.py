from cogs.commands.helpers.rolls.base_roll_helper import BaseRollHelper
import discord
from typing import Any, Type, TypeVar, Union
from db.db_handler import DbHandler
import datetime
T = TypeVar('T')

class MonthlyRollHelper(BaseRollHelper):
    def __init__(self, user: Union[discord.User, discord.Member], db: DbHandler, table: T):
        BaseRollHelper.__init__(self, user, db, table)
        
    def process_roll(self, is_lucky: bool, today_date_str: str):
        current_month = datetime.datetime.now().month
        if self.user_row.CurrentMonthNumber != current_month:
            self.user_row.CurrentMonthNumber = current_month
            self.user_row.LuckyCount = 0
            self.user_row.UnluckyCount = 0
            self.user_row.LastRoll = ""
            self.user_row.CurrentLuckyStreak = 0
            self.user_row.CurrentUnluckyStreak = 0
        super().process_roll(is_lucky, today_date_str)
    
    def build_new_user_row(self) -> T:
        row = super().build_new_user_row()
        row.CurrentMonthNumber = 0
        return row
    
    def generate_result_message(self):
        lucky_emoji = str('<:moyai_wine:1112926132883427450>')
        unlucky_emoji = str('<:peepoHorror:754067746219753472>')

        now = datetime.datetime.now()
        month = now.month
        if month == 11:
            lucky_emoji = ":turkey:"
            unlucky_emoji = ":fork_knife_plate:"
        if month == 12:
            lucky_emoji = ":christmas_tree:"
            unlucky_emoji = str('<:coal:1180190038550659082>')
            
        return super().generate_result_message(lucky_emoji, unlucky_emoji, None)
    
    def get_month(self):
        now = datetime.datetime.now()
        header = datetime.datetime.now().strftime("%B")
        return header