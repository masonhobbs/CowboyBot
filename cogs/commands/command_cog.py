import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import tree
import random
import datetime
from db.db_handler import DbHandler
from cogs.commands.models.cowboy_react import CowboyReact
from cogs.commands.models.user_luck import UserLuck
from discord.app_commands import Choice

class CommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db = db

    # syncs all commands globally
    # optional guild id to sync only a specific server
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
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        rows = self.db.get_user_luck_all()
        formatted_rows = []
        for row in rows:
            formatted_rows.append(UserLuck(row[0],row[1],row[2],row[3]))

        formatted_rows.sort(key=lambda x: x.lucky, reverse=True)
        msg = "```Lucker Dog Leaderboard\n--------------------------\n"
        for index, item in enumerate(formatted_rows):
            total = item.lucky + item.unlucky
            ratio = (float(item.lucky) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            msg = msg + str (index + 1) + '. ' + item.user + ' - ' + str(item.lucky) + ' (' + str(formatted_ratio) + ')\n'

        msg = msg + "\nBad Luck Brian Leaderboard\n--------------------------\n"
        formatted_rows.sort(key=lambda x: x.unlucky, reverse=True)
        for index, item in enumerate(formatted_rows):
            total = item.lucky + item.unlucky
            ratio = (float(item.unlucky) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            msg = msg + str (index + 1) + '. ' + item.user + ' - ' + str(item.unlucky) + ' (' + str(formatted_ratio) + ')\n'

        msg = msg + '```'
        await interaction.response.send_message(msg)

    @app_commands.command(name="roll", description="Test your luck for the day")
    async def roll(self, interaction: discord.Interaction):
        row = None
        now = datetime.datetime.now()
        seeded_datetime_string = now.strftime("%m/%d/%Y")
        seed = interaction.user.name + seeded_datetime_string
        
        luck_row = self.db.get_user_luck(interaction.user.name)
        random.seed(seed)
        roll = random.randint(0, 101)

        print(seed + ' - ' + str(roll))
        
        luckyCount = 0
        unluckyCount = 0
        if (roll > 50):
            luckyCount +=1
        elif (roll <= 50):
            unluckyCount += 1

        if len(luck_row) == 0:
            self.db.initialize_user_luck_row(interaction.user.name,luckyCount,unluckyCount)
        else:
            user_row = None
            row = luck_row[0]

            user_row = UserLuck(interaction.user.name,row[1],row[2],row[3])
            if user_row.last_roll_date != seeded_datetime_string:
                self.db.update_user_luck_row(interaction.user.name, user_row.lucky + luckyCount, user_row.unlucky + unluckyCount)

        luck_row = self.db.get_user_luck(interaction.user.name)
        row = luck_row[0]
        user_row = None
        user_row = UserLuck(interaction.user.name,row[1],row[2],row[3])

        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>')
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>')
        stat_var_message = " \n\n" + lucky_var_emoji_message + ' `' + str(user_row.lucky) + "`\t " + unlucky_var_emoji_message + '  `' + str(user_row.unlucky) + "`"
        if (roll <= 50):
            await interaction.response.send_message(unlucky_var_emoji_message + " You rolled a `1`!" + stat_var_message)
        elif (roll > 50):
            await interaction.response.send_message(lucky_var_emoji_message + " You rolled a `20`!" + stat_var_message)

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

async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        CommandCog(bot,db)
    )
        