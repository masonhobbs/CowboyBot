from discord.ext import commands
from discord.ext.commands import CommandNotFound
from db.db_handler import DbHandler
from constants.cowboy_constants import CowboyConstants

class EventCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db = db
        self.cowboy_emoji = '\U0001F920'
        self.moyai_emoji = '\U0001F5FF'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if ('"' in message.content):
            message.content = message.content.replace('"', "'")

        for trigger in CowboyConstants.cowboy_react_triggers:
            if trigger in message.content.lower() and '/cowboy' not in message.content.lower() and '!cowboy' not in message.content.lower():
                await message.add_reaction(str('<:moyai_cowboy:1112925840511094865>'))
                self.db.insert_cowboy_reacts_table('' + trigger)
                break
        
        if ("bruh" in message.content.lower() or "moment" in message.content.lower()):
            channel = message.channel
            await channel.send(str('<:moyai_cowboy:1112925840511094865>'))
            await message.add_reaction(str('<:moyai_cowboy:1112925840511094865>'))

        if ("/cowboy 1d20" in message.content.lower()):
            await message.channel.send("CowboyBot has upgraded, you must now use the in-built discord commands by typing / or /cowboy or /roll and selecting the command")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        for channel in member.guild.text_channels:
            if channel.name == 'general':
                await channel.send("Howdy " + member.mention + '! :cowboy:')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, *args):
        error = args[0]
        if isinstance(error, CommandNotFound) or ("not found" in error.lower()):
            command_name = ctx.message.content.split("/cowboy ")[1]
            self.db.insert_feature_requests_table(command_name)
            await ctx.send("i can only do so many commands, mesin pls add " + command_name + '"')


async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        EventCog(bot,db)
    )
        