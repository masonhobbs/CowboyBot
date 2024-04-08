import discord
from discord.ext import commands

TOKEN = 'YOURTOKENHERE'
ACTIVITY = discord.Game(name="Try out duels! /duel")

class CowboyBotClient(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=("!cowboy", "/cowboy"),
            intents = discord.Intents.all(),
            application_id = -1 # your app id here
        )

        self.initial_extensions = [
            "cogs.commands.command_cog",
            "cogs.commands.duel_cog",
            "cogs.events.event_cog"            
        ]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            print(extension)
            await self.load_extension(extension)

 
    async def on_ready(self):
        await self.change_presence(activity=ACTIVITY)
        print(f'{self.user} has connected to Discord!')

bot = CowboyBotClient()
bot.run(TOKEN)