import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
import sys
from db.db_handler import DbHandler
from cogs.events.event_cog import EventCog
from cogs.commands.command_cog import CommandCog
from cogs.commands.duel_cog import DuelCog
import asyncio
from discord import app_commands

BOT_PREFIX=("!cowboy ","/cowboy ", "/cowboybot ", "!cowboybot ")
TOKEN = 'YOURTOKENHERE'

class CowboyBotClient(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=("!cowboy", "/cowboy"),
            intents = discord.Intents.all(),
            application_id = -1 # your app_id here
        )

        self.initial_extensions = [
            "cogs.commands.command_cog",
            "cogs.events.event_cog"            
        ]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await bot.tree.sync(guild=discord.Object(id = -1)) # your guild id here

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

bot = CowboyBotClient()
bot.run(TOKEN)