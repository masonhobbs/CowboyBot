from discord.ext import commands
import random
from datetime import datetime
from cogs.commands.models.cowboy_react import CowboyReact
from cogs.commands.models.user_luck import UserLuck

class CommandCog(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(name = "howdy")
    async def howdy(self,ctx,*args):
        msg = ""
        if len(args) > 0:
            search_param = " ".join(args[:])

            if "@everyone" in search_param or "@here" in search_param:
                await ctx.send("stop pinging everyone you clown")
                return

            foundUser = None
            for user in ctx.guild.members:
                if user.name.lower() == search_param.lower():
                    msg = 'Howdy ' + user.mention + '! :cowboy:'
                    foundUser = user
            if foundUser is None:
                msg = "who in tarnation are ya trying to find there pardner?? ain't no cowboy round these parts named " + search_param
        else:
            msg = 'Howdy ' + ctx.author.mention + '! :cowboy:'
        
        await ctx.send(msg)
        return

    @commands.command(name = "leaderboard")
    async def leaderboard(self, ctx):
        rows = self.db.get_user_luck_all()
        formatted_rows = []
        for row in rows:
            formatted_rows.append(UserLuck(row[0],row[1],row[2],row[3]))

        formatted_rows.sort(key=lambda x: x.lucky, reverse=True)
        msg = "```Lucker Dog Leaderboard\n--------------------------\n"
        for index, item in enumerate(formatted_rows):
            msg = msg + str (index + 1) + '. ' + item.user + ' - ' + str(item.lucky) + '\n'

        msg = msg + "\nBad Luck Brian Leaderboard\n--------------------------\n"
        formatted_rows.sort(key=lambda x: x.unlucky, reverse=True)
        for index, item in enumerate(formatted_rows):
            msg = msg + str (index + 1) + '. ' + item.user + ' - ' + str(item.unlucky) + '\n'

        msg = msg + '```'
        await ctx.send(msg)
        

    @commands.command(name = "1d20")
    async def roll(self, ctx, *args):
        row = None
        now = datetime.now()
        seeded_datetime_string = now.strftime("%m/%d/%Y")
        seed = ctx.author.name + seeded_datetime_string
        
        luck_row = self.db.get_user_luck(ctx.author.name)
        random.seed(seed)
        roll = random.randint(0, 1)

        luckyCount = 0
        unluckyCount = 0
        if (roll == 1):
            luckyCount +=1
        else:
            unluckyCount += 1

        if len(luck_row) == 0:
            self.db.initialize_user_luck_row(ctx.author.name,luckyCount,unluckyCount)
        else:
            user_row = None
            row = luck_row[0]

            user_row = UserLuck(ctx.author.name,row[1],row[2],row[3])
            if user_row.last_roll_date != seeded_datetime_string:
                self.db.update_user_luck_row(ctx.author.name, user_row.lucky + luckyCount, user_row.unlucky + unluckyCount)

        luck_row = self.db.get_user_luck(ctx.author.name)
        row = luck_row[0]
        user_row = None
        user_row = UserLuck(ctx.author.name,row[1],row[2],row[3])

        if (roll == 0):
            await ctx.send("You rolled a [1]! \n`Lucky days: " + str(user_row.lucky) + " | Unlucky days: " + str(user_row.unlucky) + '`')
        else:
            await ctx.send("You rolled a [20]! \n`Lucky days: " + str(user_row.lucky) + " | Unlucky days: " + str(user_row.unlucky) + '`')

        
    @commands.command(name = "reactcount")
    async def reactcount(self,ctx, arg = None):
        react_rows = self.db.get_cowboy_reacts_count()
        total_react_count = len(self.db.get_cowboy_reacts())
        sorted_count_list = []
        for row in react_rows:
            entry = CowboyReact(row[0], row[1])
            sorted_count_list.append(entry)

        sorted_count_list.sort(key=lambda x: x.count, reverse=True)
        if len(sorted_count_list) == 0:
            await ctx.send("Could not obtain cowboy word list, sad yeehaw")
            return
        
        msg = ""

        if arg == 'top':    
            top_entry = sorted_count_list[0]
            msg = "The top cowboy word is `" + top_entry.trigger_word + "`, occurring " + str(top_entry.count) + " times"
            await ctx.send(msg)
        elif arg == 'bottom':
            bottom_entry = sorted_count_list[-1]
            msg = "The bottom cowboy word is `" + bottom_entry.trigger_word + "`, occurring " + str(bottom_entry.count) + " times"
            await ctx.send(msg)
        elif arg == 'all':
            msg = "```\n"
            try:
                for index, item in enumerate(sorted_count_list):
                    msg = msg + str(index + 1) + '. ' + item.trigger_word + ', ' + str(item.count) + ' times\n'
                msg = msg + "\nTotal: " + str(total_react_count) + " times" + "\n```"
                await ctx.send(msg)
            except Exception as e:
                print(e)
        else:
            msg = 'I have reacted to ' + str(total_react_count) + ' cowboy messages'
            await ctx.send(msg)

    @commands.command(name = "requestfeature")
    async def add_feature_request(self,ctx,*args):
        feature_to_add = " ".join(args[:])
        self.db.insert_feature_requests_table(feature_to_add)
        await ctx.send("Feature request added!")

    @commands.command(name = "getfeaturerequests")
    async def get_feature_requests(self,ctx):
        features = self.db.get_feature_requests()
        await ctx.send(features)