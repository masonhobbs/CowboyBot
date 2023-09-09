from typing import List
import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime
from db.db_handler import DbHandler
from db.models.cowboy_react import CowboyReact
from discord.app_commands import Choice
from cogs.commands.ui.views.pageable_embed_view import PageableEmbedView
from cogs.commands.helpers.rolls.leaderboard_helper import Leaderboard_Helper
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
        if interaction.user.id == 350035723329470465:
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
        now = datetime.datetime.now()
        month_title = now.strftime("%B") + " " + str(now.year) + " Leaderboard"
        leaderboard_helper = Leaderboard_Helper()
        overall_embed = leaderboard_helper.build_leaderboard_embed("Overall Leaderboard", list(self.db.session.scalars(select(UserIdLuck)).all()), discord.Color.dark_gold())
        monthly_embed = leaderboard_helper.build_leaderboard_embed(month_title, list(self.db.session.scalars(select(UserIdMonthlyLuck).where(UserIdMonthlyLuck.CurrentMonthNumber == now.month)).all()), discord.Color.dark_blue())
        embeds = [overall_embed, monthly_embed]
        start_embed_index = 0
        if display_monthly_leaderboard is True:
            start_embed_index = 1

        view = PageableEmbedView(embeds, start_page=start_embed_index)
        await interaction.response.send_message(embed=embeds[start_embed_index],view=view)

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

    # This is basically just a dev command to test out random stuff
    @app_commands.command(name="sandbox", description="For dev testing whatever code is contained in this command")
    async def sandbox(self, interaction: discord.Interaction):
        result_msg = "$ some test"
        if interaction.user.id != 350035723329470465:
            await interaction.response.send_message("u ain't allowed")
            return
        await interaction.response.send_message(result_msg)
        return

async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        CommandCog(bot,db)
    )
        