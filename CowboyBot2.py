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

BOT_PREFIX=("!cowboy ","/cowboy ", "/cowboybot ", "!cowboybot ")
TOKEN = 'YOURTOKENEHRE'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)


async def setup():
    db = DbHandler()
    eventcog = asyncio.create_task(bot.add_cog(EventCog(bot,db)))
    commandcog = asyncio.create_task(bot.add_cog(CommandCog(bot,db)))
    duelcog = asyncio.create_task(bot.add_cog(DuelCog(bot,db)))
    botstart = asyncio.create_task(bot.start(TOKEN))
    
    await eventcog
    await commandcog
    await duelcog
    await botstart

asyncio.run(setup())