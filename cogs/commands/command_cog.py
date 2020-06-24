import discord
from discord.ext import commands
import sys

class CommandCog(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(name = "oof")
    async def oof(self,ctx):
        await ctx.send("oof pardner")
        return
        
    @commands.command(name = "howdy")
    async def howdy(self,ctx,*args):
        msg = ""
        print("howdy")
        print(args)
        if len(args) > 0:
            search_param = " ".join(args[:])
            if "gaming" in search_param:
                await ctx.send("fuk u, u already know i cant find gaming")
                return

            if "@everyone" in search_param or "@here" in search_param:
                await ctx.send("stop pinging every1 you clown")
                return

            user = None
            for guild in self.bot.guilds:
                user = guild.get_member_named(search_param)
                if user is not None:
                    msg = 'Howdy ' + user.mention + '! :cowboy:'
                    break
            if user is None:
                msg = "who in tarnation are ya trying to find there pardner?? ain't no cowboy round these parts named " + search_param
        else:
            msg = 'Howdy ' + ctx.author.mention + '! :cowboy:'
        
        print(msg)
        await ctx.send(msg)
        return

    @commands.command(name = "reactcount")
    async def reactcount(self,ctx, arg = None):
        cowboy_reacts = self.db.get_cowboy_reacts()
        msg = ""
        if arg == 'top':    
            counter = 0
            react = cowboy_reacts[0] 
            
            for i in cowboy_reacts: 
                curr_frequency = cowboy_reacts.count(i)
                if(curr_frequency > counter): 
                    counter = curr_frequency 
                    react = i

            msg = "The top cowboy word is " + str(react) + ", occurring " + str(counter) + " times"
            await ctx.send(msg)
            return
        elif arg == 'bottom':
            print("hlleo")
            counter = sys.maxsize
            react = cowboy_reacts[0] 
            
            for i in cowboy_reacts: 
                curr_frequency = cowboy_reacts.count(i)
                if(curr_frequency < counter): 
                    counter = curr_frequency 
                    react = i
                    print("new bottom: " + str(react))

            msg = "The bottom cowboy word is " + str(react) + ", occurring " + str(counter) + " times"
            await ctx.send(msg)
            return

        else:
            msg = 'I have reacted to ' + str(len(cowboy_reacts)) + ' cowboy messages'
            await ctx.send(msg)
            return