from cogs.commands.helpers.rolls.base_roll_helper import BaseRollHelper
import discord
from typing import Any, Type, TypeVar, Union
from cogs.commands.helpers.rolls.monthly_roll_emoji_helper import MonthlyRollEmojiHelper
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
        monthly_roll_emoji_helper = MonthlyRollEmojiHelper()
        month_lucky_emoji = monthly_roll_emoji_helper.get_month_lucky_emoji()
        month_unlucky_emoji = monthly_roll_emoji_helper.get_month_unlucky_emoji()
        return super().generate_result_message(month_lucky_emoji, month_unlucky_emoji, None)
    
    def get_month(self):
        now = datetime.datetime.now()
        header = datetime.datetime.now().strftime("%B")
        return header
        