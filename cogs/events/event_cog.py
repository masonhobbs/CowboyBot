from discord.ext import commands
from discord.ext.commands import CommandNotFound

class EventCog(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.cowboy_react_triggers = ['howdy', 'yeehaw', 'pardner', 'buckaroo', 'cowboy', 'what in tarnation', 'rancher', 'beans', 'biscuits','biscuit',
                                      'wrangler', 'rodeo', 'gunslinger', 'hillbilly', 'tootin', 'rootin', 'cowgirl', 'texas']
        self.db = db
        self.cowboy_emoji = '\U0001F920'
        self.moyai_emoji = '\U0001F5FF'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if ('"' in message.content):
            message.content = message.content.replace('"', "'")

        for trigger in self.cowboy_react_triggers:
            if trigger in message.content.lower() and '/cowboy' not in message.content.lower() and '!cowboy' not in message.content.lower():
                await message.add_reaction(self.cowboy_emoji)
                self.db.insert_cowboy_reacts_table('' + trigger)
                break
        
        if ("bruh" in message.content.lower() or "moment" in message.content.lower()):
            channel = message.channel
            await channel.send(':moyai:')
            await message.add_reaction(self.moyai_emoji)


    @commands.Cog.listener()
    async def on_member_join(self,member):
        for channel in member.guild.text_channels:
            if channel.name == 'general':
                await channel.send("Howdy " + member.mention + '! :cowboy:')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, *args):
        error = args[0]
        if isinstance(error, CommandNotFound) or ("not found" in error.lower()):
            if ctx.author.name.lower() == "mesin":
                command_name = ctx.message.content.split("/cowboy ")[1]
                self.db.insert_feature_requests_table(command_name)
                await ctx.send("i can only do so many commands, " + ctx.author.mention + ' pls add "' + command_name + '"')

        