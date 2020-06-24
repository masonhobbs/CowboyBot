from discord.ext import commands
from discord.ext.commands import CommandNotFound

class EventCog(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.cowboy_react_triggers = ['howdy', 'yeehaw', 'pardner', 'buckaroo', 'cowboy', 'what in tarnation']
        self.db = db
        self.cowboy_emoji = '\U0001F920'

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

    @commands.Cog.listener()
    async def on_member_join(self,member):
        channel = member.guild.text_channels[0]
        await channel.send("Howdy " + member.mention + '! :cowboy:')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            for guild in self.bot.guilds:
                user = guild.get_member_named('mesinhibbs')
                if user is not None:
                    command_name = ctx.message.content.split("/cowboy ")[1]
                    await ctx.send("i can only do so many commands, " + user.mention + ' pls add "' + command_name + '"')

        