import discord
from discord.ext import commands
import random
import datetime
from cogs.commands.models.cowboy_react import CowboyReact
from cogs.commands.models.user_luck import UserLuck

class CommandCog(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.clover_emoji = '\U0001F340'
        self.unlucky_emoji = '\U0001F6AB'

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
            total = item.lucky + item.unlucky
            ratio = (float(item.lucky) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            msg = msg + str (index + 1) + '. ' + item.user + ' - ' + str(item.lucky) + ' (' + str(formatted_ratio) + ')\n'

        msg = msg + "\nBad Luck Brian Leaderboard\n--------------------------\n"
        formatted_rows.sort(key=lambda x: x.unlucky, reverse=True)
        for index, item in enumerate(formatted_rows):
            total = item.lucky + item.unlucky
            ratio = (float(item.unlucky) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            msg = msg + str (index + 1) + '. ' + item.user + ' - ' + str(item.unlucky) + ' (' + str(formatted_ratio) + ')\n'

        msg = msg + '```'
        await ctx.send(msg)
        

    @commands.command(name = "1d20")
    async def roll(self, ctx, *args):
        row = None
        now = datetime.datetime.now()
        seeded_datetime_string = now.strftime("%m/%d/%Y")
        seed = ctx.author.name + seeded_datetime_string
        
        luck_row = self.db.get_user_luck(ctx.author.name)
        random.seed(seed)
        roll = random.randint(0, 101)

        print(seed + ' - ' + str(roll))
        
        luckyCount = 0
        unluckyCount = 0
        if (roll > 50):
            luckyCount +=1
        elif (roll <= 50):
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

        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>')
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>')
        stat_var_message = " \n\n" + lucky_var_emoji_message + ' `' + str(user_row.lucky) + "`\t " + unlucky_var_emoji_message + '  `' + str(user_row.unlucky) + "`"
        if (roll <= 50):
            await ctx.send(unlucky_var_emoji_message + " You rolled a `1`!" + stat_var_message)
        elif (roll > 50):
            await ctx.send(lucky_var_emoji_message + " You rolled a `20`!" + stat_var_message)

        
    @commands.command(name = "destiny")
    async def destiny(self,ctx,*args):
        lucky_days = 0
        unlucky_days = 0
        the_day = datetime.datetime.now()
        seeded_datetime_string = the_day.strftime("%m/%d/%Y")
        seed = args[0] + seeded_datetime_string
        random.seed(seed)
        roll = random.randint(0, 101)
        print(seed + str(roll))
        if (roll <= 50):
            unlucky_days += 1
        elif (roll > 50):
            lucky_days += 1

        try:
            for i in range(int(args[1])):
                try:
                    the_day += datetime.timedelta(days=1)
                    seeded_datetime_string = the_day.strftime("%m/%d/%Y")
                    seed = args[0] + seeded_datetime_string
                    random.seed(seed)
                    roll = random.randint(0, 101)
                    print(seed + ' ' + str(roll))
                    if (roll <= 50):
                        unlucky_days += 1
                    elif (roll > 50):
                        lucky_days += 1
                except Exception as e:
                    print(e)

            print("user - " + args[0]    + " - lucky days: " + str(lucky_days) + " - unlucky days: " + str(unlucky_days))
        except Exception as e:
            print(e)

        await ctx.send("Logged to console")

    @commands.command(name = "test")
    async def test(self,ctx):
        print(ctx.message)
        emoji = discord.utils.get(self.bot.emojis, name='pensiveCowboy')
        for emoji in self.bot.emojis:
            print(emoji)
        await ctx.send(str('<a:moyai_dance:1112929694241783918>'))
        await ctx.message.add_reaction(str('<:moyai_cowboy:1112925840511094865>'))
        # await ctx.send("this is for whatever my dumbfuck creator is testing")

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