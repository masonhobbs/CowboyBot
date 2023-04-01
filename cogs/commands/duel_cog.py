import discord
from discord.ext import commands
import sys

class DuelCog(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(name = "duel")
    async def duel(self,ctx,*args):
        challenger = ctx.message.author
        opponent = None

        if len(args) > 0:
            for guild in self.bot.guilds:
                search_param = " ".join(args[:])
                members = await guild.fetch_members().flatten()
                for member in members:
                    if member.name.lower() == search_param.lower():
                        opponent = member
                if opponent is not None:
                    break

            if opponent.name.lower() == 'CowboyBot'.lower() :
                await ctx.send('*quick draws on your ass* gg pardner')
                return
            if opponent is not None:
                if opponent.name.lower() == challenger.name.lower():
                    await ctx.send("yeehaw you can't duel yerself pardner")
                    return

                await ctx.send('Yeehaw ' + opponent.mention + '! ' + challenger.name + ' has challenged you to duel! Do you accept? (y/n)')
                try:
                    def check(message):
                        if message.author.name != opponent.name:
                            return
                        return message.author.name == opponent.name

                    opponent_response = await self.bot.wait_for('message', check=check, timeout=30)
                    opponent_response.content = opponent_response.content.lower()
                    if opponent_response.content == 'y' or opponent_response.content == 'yes':
                        await ctx.send('cool')
                    elif opponent_response.content == 'n' or opponent_response.content == 'no':
                        await ctx.send('dang ol coward pardner')
                    else:
                        await ctx.send("bad response. you lose idiot")
                except:
                    await ctx.send(opponent.name + ' did not respond in time')
            else:
                await ctx.send("Could not find that cowboy 'round these parts")
                return

        else:
            await ctx.send('usage: /cowboy duel <opponent name>')
            return
            
    
