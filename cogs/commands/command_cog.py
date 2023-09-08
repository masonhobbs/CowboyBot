from typing import List
import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime
from db.db_handler import DbHandler
from db.models.cowboy_react import CowboyReact
from discord.app_commands import Choice
from cogs.commands.helpers.rolls.base_roll_helper import BaseRollHelper
from cogs.commands.helpers.rolls.monthly_roll_helper import MonthlyRollHelper

from sqlalchemy import select
from db.tables.user_id_luck import UserIdLuck
from db.tables.user_id_monthly_luck import UserIdMonthlyLuck

class CommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db: DbHandler = db

    @app_commands.command(name="sync", description="For syncing slash commands, dev only")
    @app_commands.describe(guild_id = "The guild id to sync")
    async def sync(self, interaction: discord.Interaction, guild_id: str = None) -> None:
        if interaction.user.id == -1:
            try:
                if (guild_id is None):
                    await self.bot.tree.sync()
                else:
                    await self.bot.tree.sync(guild=discord.Object(id=int(guild_id)))
                await interaction.response.send_message("Commands synced across servers")
            except Exception as e:
                print(e)

        else:
            await interaction.response.send_message("You must be the bot developer to use this command, go away")

    @app_commands.command(name="howdy", description="Get greeted with a hearty howdy")    
    @app_commands.describe(person = "The person you would like to greet")
    async def howdy(self, interaction: discord.Interaction, person: discord.Member) -> None:
        await interaction.response.send_message(f"Howdy {person.mention}! :cowboy:")

    @app_commands.command(name="leaderboard", description="Show leaderboard for 1d20 rolls")
    @app_commands.describe(display_monthly_leaderboard = "Display monthly leaderboard instead")
    async def leaderboard(self, interaction: discord.Interaction, display_monthly_leaderboard: bool = None) -> None:
        rows = []
        msg = ""
        if display_monthly_leaderboard is None or display_monthly_leaderboard is False:
            rows: List[UserIdLuck] = list(self.db.session.scalars(select(UserIdLuck)).all())
        elif display_monthly_leaderboard is True:
            current_month = datetime.datetime.now().month
            rows: List[UserIdMonthlyLuck] = list(self.db.session.scalars(select(UserIdMonthlyLuck).where(UserIdMonthlyLuck.CurrentMonthNumber == current_month)).all())
            
        num_lucky_users = 0
        num_lucky_rolls = 0
        num_unlucky_users = 0
        num_unlucky_rolls = 0
        total_rolls = 0
        rows.sort(key=lambda x: x.LuckyCount, reverse=True)
        if display_monthly_leaderboard is True:
            now = datetime.datetime.now()
            month_name = now.strftime("%B")
            msg = "```" + month_name + " " + str(now.year) + " Leaderboard\n\n" + "Lucker Dog Leaderboard\n--------------------------\n"
        else:
            msg = "```Lucker Dog Leaderboard\n--------------------------\n"
            
        for index, item in enumerate(rows):
            total = item.LuckyCount + item.UnluckyCount
            ratio = (float(item.LuckyCount) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            msg = msg + str (index + 1) + '. ' + item.Username + ' - ' + str(item.LuckyCount) + ' (' + str(formatted_ratio) + ')\n'
            total_rolls += item.LuckyCount
            num_lucky_rolls += item.LuckyCount
            num_lucky_users += 1

        msg = msg + "\nBad Luck Brian Leaderboard\n--------------------------\n"
        rows.sort(key=lambda x: x.UnluckyCount, reverse=True)
        for index, item in enumerate(rows):
            total = item.LuckyCount + item.UnluckyCount
            ratio = (float(item.UnluckyCount) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            msg = msg + str (index + 1) + '. ' + item.Username + ' - ' + str(item.UnluckyCount) + ' (' + str(formatted_ratio) + ')\n'

            total_rolls += item.UnluckyCount
            num_unlucky_rolls += item.UnluckyCount
            num_unlucky_users += 1

        average_lucky_percent = (float(num_lucky_rolls) / float(total_rolls))
        average_unlucky_percent = (float(num_unlucky_rolls) / float(total_rolls))
        formatted_lucky_percent = "{:.1%}".format(average_lucky_percent)
        formatted_unlucky_percent = "{:.1%}".format(average_unlucky_percent)
        msg = msg + '\nTotal rolls: ' + str(total_rolls) + ' | Overall lucky rolls: ' + formatted_lucky_percent + ' | Overall unlucky rolls: ' + formatted_unlucky_percent + '```'
        await interaction.response.send_message(msg)

    @app_commands.command(name="roll", description="Test your luck for the day")
    async def roll(self, interaction: discord.Interaction):
        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>')
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>')
        now = datetime.datetime.now()
        today_date_str = now.strftime("%m/%d/%Y")
        seed = str(interaction.user.id) + today_date_str
        random.seed(seed)
        is_lucky = random.randint(0, 1) == 1

        try:
            overall_roller = BaseRollHelper(interaction.user, self.db, UserIdLuck)            
            monthly_roller = MonthlyRollHelper(interaction.user, self.db, UserIdMonthlyLuck)

            if overall_roller.has_already_rolled(today_date_str) is True:
                if is_lucky is True:
                    result_already_rolled = '[20]'
                else:
                    result_already_rolled = '[1]'
                await interaction.response.send_message("You already rolled today, pardner! (You rolled a `" + result_already_rolled + "`!)")
                return

            overall_roller.process_roll(is_lucky, today_date_str)
            monthly_roller.process_roll(is_lucky, today_date_str)
            
            response_message = overall_roller.generate_result_message(lucky_var_emoji_message, unlucky_var_emoji_message, None) + monthly_roller.generate_result_message()

            if is_lucky is False:
                await interaction.response.send_message(unlucky_var_emoji_message + " You rolled a `1`!  (" + str(overall_roller.user_row.CurrentUnluckyStreak) + "x unlucky streak)" + response_message)
            elif is_lucky is True:
                await interaction.response.send_message(lucky_var_emoji_message + " You rolled a `20`!   (" + str(overall_roller.user_row.CurrentLuckyStreak) + "x lucky streak)" + response_message)
        except Exception as e: 
            await interaction.response.send_message("oops things got fucked because i tried to get fancy, i'll fix it soon tm")

    @app_commands.command(name="react_count", description="See the number of messages that CowboyBot has reacted to")    
    @app_commands.describe(type = "See the most used cowboy word, the least used, or show the list of all cowboy words and their frequency")
    @app_commands.choices(type = [
        Choice(name = "All", value = "all"),
        Choice(name = "Most Used", value = "top"),
        Choice(name = "Least Used", value = "bottom")
    ])
    async def reactcount(self, interaction: discord.Interaction, type: str) -> None:
        react_rows = self.db.get_cowboy_reacts_count()
        total_react_count = len(self.db.get_cowboy_reacts())
        sorted_count_list = []
        for row in react_rows:
            entry = CowboyReact(row[0], row[1])
            sorted_count_list.append(entry)

        sorted_count_list.sort(key=lambda x: x.count, reverse=True)
        if len(sorted_count_list) == 0:
            await interaction.response.send_message("Could not obtain cowboy word list, sad yeehaw")
            return
        
        msg = ""

        if type == 'top':    
            top_entry = sorted_count_list[0]
            msg = "The top cowboy word is `" + top_entry.trigger_word + "`, occurring " + str(top_entry.count) + " times"
            await interaction.response.send_message(msg)
        elif type == 'bottom':
            bottom_entry = sorted_count_list[-1]
            msg = "The bottom cowboy word is `" + bottom_entry.trigger_word + "`, occurring " + str(bottom_entry.count) + " times"
            await interaction.response.send_message(msg)
        elif type == 'all':
            msg = "```\n"
            try:
                for index, item in enumerate(sorted_count_list):
                    msg = msg + str(index + 1) + '. ' + item.trigger_word + ', ' + str(item.count) + ' times\n'
                msg = msg + "\nTotal: " + str(total_react_count) + " times" + "\n```"
                await interaction.response.send_message(msg)
            except Exception as e:
                print(e)

    @app_commands.command(name="sandbox", description="For dev testing whatever code is contained in this command")
    async def sandbox(self, interaction: discord.Interaction):
        result_msg = "$"
        if interaction.user.id != -1:
            await interaction.response.send_message("u ain't allowed")
            return

        today_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        overall_rolls = BaseRollHelper(interaction.user, self.db, UserIdLuck)
        overall_rolls.process_roll(False, today_date_str)
        await interaction.response.send_message(result_msg)
        return

async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        CommandCog(bot,db)
    )
        