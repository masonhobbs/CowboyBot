import discord
from typing import List, Union

from cogs.commands.helpers.common.name_helper import NameHelper

class RollResultView(discord.ui.View):
    def __init__(self, lucky: bool, saving_throw: bool, roll_totals_with_emojis: str, roll_streak: int, already_rolled: bool):
        super().__init__(timeout=None)
        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>')
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>')
        self.already_rolled = already_rolled
        self.embed: discord.Embed = discord.Embed(title="Roll!",color=discord.Color.dark_green())
        if already_rolled is False:
            streak_type: str = None
            if (lucky):
                self.embed.title = lucky_var_emoji_message + " You rolled a 20!"
                streak_type = "Lucky streak"
                if (saving_throw):
                    self.embed.color = discord.Color.dark_gold()
                    self.embed.title = self.embed.title + " Saving throw success!"
            else:
                self.embed.title = unlucky_var_emoji_message + " You rolled a 1!"
                streak_type = "Unlucky streak"
                self.embed.color = discord.Color.dark_red()


            self.embed.add_field(name="Result", value=roll_totals_with_emojis, inline=True)
            self.embed.set_footer(text=(str(roll_streak) + "x " + streak_type))
        else:
            self.embed.title = None
            self.embed.color = discord.Color.dark_teal()
            self.embed.add_field(name="Already rolled!",value="You already rolled today! It was a " + str("20" if lucky else "1") + ".")

    def add_special_leaderboard_result(self, type: str, message: str):
        if self.already_rolled is False:
            self.embed.add_field(name=type, value=message, inline=False)
        return
    
    def get_embed(self): 
        return self.embed
    
    def add_author(self, user: Union[discord.User, discord.Member]):
        name_helper = NameHelper(user)
        author = name_helper.get_user_name()
        self.embed.set_author(name=author)
    