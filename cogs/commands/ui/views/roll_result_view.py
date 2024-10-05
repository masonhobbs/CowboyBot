import discord
from typing import List, Union

from cogs.commands.helpers.common.name_helper import NameHelper

class RollResultView(discord.ui.View):
    def __init__(self, lucky: bool, saving_throw: bool, saving_fail: bool, roll_totals_with_emojis: str, roll_streak: int, already_rolled: bool, lucky_emoji_override: str | None, unlucky_emoji_override: str | None):
        super().__init__(timeout=None)
        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>') + " "
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>') + " "

        if (lucky_emoji_override is not None):
            lucky_var_emoji_message = str(lucky_emoji_override) + " "
        if (unlucky_emoji_override is not None):
            unlucky_var_emoji_message = str(unlucky_emoji_override) + " "

        self.already_rolled = already_rolled
        self.embed: discord.Embed = discord.Embed(color=discord.Color.dark_green() if lucky else discord.Color.dark_red())
        if already_rolled is False:
            streak_type: str = "lucky streak" if lucky else "unlucky streak"
            self.embed.description = lucky_var_emoji_message + "**You rolled a 20!**" if lucky else unlucky_var_emoji_message + "**You rolled a 1!**"
            if (saving_throw):
                self.embed.color = discord.Color.dark_gold()
                self.embed.description = self.embed.title + " Critical success!"
            if (saving_fail):
                self.embed.description = unlucky_var_emoji_message + " Unlucky! Critical fail! You should roll a 1 NOW!"
                self.embed.color = discord.Color.dark_magenta()
            
            self.embed.add_field(name="Overall", value=roll_totals_with_emojis, inline=True)
            self.embed.set_footer(text=(str(roll_streak) + "x " + streak_type))
        else:
            self.embed.title = None
            self.embed.color = discord.Color.dark_teal()
            self.embed.add_field(name="Already rolled!",value="You already rolled today! It was a " + str("20" if lucky and saving_fail is False else "1") + ".")

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
    