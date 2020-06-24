import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
import sys
from db.db_handler import DbHandler
from cogs.events.event_cog import EventCog
from cogs.commands.command_cog import CommandCog

BOT_PREFIX=("!cowboy ","/cowboy ")
TOKEN = 'XXXXXXXXX'
bot = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True)
db = DbHandler()

bot.add_cog(EventCog(bot,db))
bot.add_cog(CommandCog(bot,db))
print("cogs added")
bot.run(TOKEN)