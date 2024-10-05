import discord
from discord import app_commands
from discord.ext import commands
from db.db_handler import DbHandler
from db.models.cowboy_react import CowboyReact
from discord.app_commands import Choice
from sqlalchemy import select, insert
from db.tables.feature_request import FeatureRequests

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

    @app_commands.command(name="sellout", description="big money baby")
    async def sellout(self, interaction: discord.Interaction) -> None:
        message = "Discover Bearserker Gummies – the ultimate pre-workout supplement infused with powerful ingredients to boost your energy and performance. Perfect for athletes, bodybuilders, and gym-goers of all levels. Enjoy the convenience of delicious sour gummies that fuel your fitness journey. Join the Bearserker community today"
        message = message + "\n\nhttps://bearserkergummies.com/"
        await interaction.response.send_message(message)

    @app_commands.command(name="request_feature", description="Submit ideas for the next evolution of CowboyBot")
    @app_commands.describe(idea = "Submit your idea")
    async def submit_feature(self, interaction: discord.Interaction, idea: str) -> None:
        print(idea)
        try:
            if idea is None or len(idea) == 0:
                await interaction.response.send_message("You did not provide an idea pardner!")
                return
            
            insert_statement = insert(FeatureRequests).values(Request=idea, User=interaction.user.name)
            with self.db.engine.connect() as conn:
                result = conn.execute(insert_statement)
                conn.commit()
                print(result)
                await interaction.response.send_message("Your request has been submitted!")
        except Exception as e:
            print(e) 

    @app_commands.command(name="features", description="See all feature requests for the next evolution of CowboyBot")
    async def get_features(self, interaction: discord.Interaction) -> None:
        features = self.db.session.scalars(select(FeatureRequests)).all()
        msg = "`"
        for item in features:
            feature: FeatureRequests = item
            msg = msg + str(feature.Id) + ". " + feature.Request + " - by " + feature.User + "\n"

        msg = msg + "`"
        await interaction.response.send_message(msg)

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
        if interaction.user.id != 350035723329470465:
            await interaction.response.send_message("u ain't allowed")
            return
        
        result = "sandbox"
        
        await interaction.response.send_message(result)
        return
    

async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        CommandCog(bot,db)
    )
        