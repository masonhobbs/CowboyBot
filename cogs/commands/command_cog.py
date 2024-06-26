import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime
from cogs.commands.helpers.common.discord_image_file_helper import DiscordImageFileHelper
from cogs.commands.helpers.common.name_helper import NameHelper
from cogs.commands.helpers.rolls.roll_log_image_helper import RollLogImageHelper
from cogs.commands.ui.views.models.pageable_embed_item import PageableEmbedItem
from db.db_handler import DbHandler
from db.models.cowboy_react import CowboyReact
from discord.app_commands import Choice
from cogs.commands.ui.views.pageable_embed_view import PageableEmbedView
from cogs.commands.helpers.rolls.leaderboard_helper import Leaderboard_Helper
from cogs.commands.helpers.rolls.base_roll_helper import BaseRollHelper
from cogs.commands.helpers.rolls.monthly_roll_helper import MonthlyRollHelper
from cogs.commands.ui.views.roll_result_view import RollResultView
import traceback

from sqlalchemy import select, insert
from db.tables.roll_logs import RollLogs
from db.tables.user_id_luck import UserIdLuck
from db.tables.user_id_monthly_luck import UserIdMonthlyLuck
from db.tables.feature_request import FeatureRequests
from db.tables.roll_streak_record import RollStreakRecord

class CommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db: DbHandler = db

    @app_commands.command(name="sync", description="For syncing slash commands, dev only")
    @app_commands.describe(guild_id = "The guild id to sync")
    async def sync(self, interaction: discord.Interaction, guild_id: str = None) -> None:
        if interaction.user.id == 350035723329470465:
            try:
                if (guild_id is None):
                    await self.bot.tree.sync()
                else:
                    await self.bot.tree.sync(guild=discord.Object(id=int(guild_id)))
                await interaction.response.send_message("Commands synced across servers")
            except Exception as e:
                print(e)

        else:
            await interaction.response.send_message("You must be the bot developer to use this command, go away")

    @app_commands.command(name="howdy", description="Get greeted with a hearty howdy")    
    @app_commands.describe(person = "The person you would like to greet")
    async def howdy(self, interaction: discord.Interaction, person: discord.Member) -> None:
        await interaction.response.send_message(f"Howdy {person.mention}! :cowboy:")

    @app_commands.command(name="leaderboard", description="Show leaderboard for 1d20 rolls")
    @app_commands.choices(type = [
        Choice(name = "Normal", value = "normal"),
        Choice(name = "Monthly", value = "monthly"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, type: str = None) -> None:
        now = datetime.datetime.now()
        month_title = now.strftime("%B") + " " + str(now.year) + " Leaderboard"
        embeds: list[PageableEmbedItem] = []
        streak_record = self.db.session.scalars(select(RollStreakRecord)).first()

        leaderboard_helper = Leaderboard_Helper()
        
        overall_embed = leaderboard_helper.build_leaderboard_embed("Overall Leaderboard", list(self.db.session.scalars(select(UserIdLuck)).all()), discord.Color.dark_gold(), streak_record)
        overall_embed_item = PageableEmbedItem(overall_embed)
        embeds.append(overall_embed_item)

        monthly_embed = leaderboard_helper.build_leaderboard_embed(month_title, list(self.db.session.scalars(select(UserIdMonthlyLuck).where(UserIdMonthlyLuck.CurrentMonthNumber == now.month)).all()), discord.Color.dark_blue(), streak_record)
        monthly_embed_item = PageableEmbedItem(monthly_embed)
        embeds.append(monthly_embed_item)

        start_embed_index = 0
        if type == "monthly":
            start_embed_index = 1

        view = PageableEmbedView(embeds, start_page=start_embed_index)
        await interaction.response.send_message(embed=view.get_current_embed().get_embed(),view=view)


    @app_commands.command(name="request_feature", description="Submit ideas for the next evolution of CowboyBot")
    @app_commands.describe(idea = "Submit your idea")
    async def submit_feature(self, interaction: discord.Interaction, idea: str) -> None:
        print(idea)
        try:
            if idea is None or len(idea) == 0:
                await interaction.response.send_message("You did not provide an idea pardner!")
                return
            
            insert_statement = insert(FeatureRequests).values(Request=idea, User=interaction.user.name)
            with self.db.engine.connect() as conn:
                result = conn.execute(insert_statement)
                conn.commit()
                print(result)
                await interaction.response.send_message("Your request has been submitted!")
        except Exception as e:
            print(e) 

    @app_commands.command(name="features", description="See all feature requests for the next evolution of CowboyBot")
    async def get_features(self, interaction: discord.Interaction) -> None:
        features = self.db.session.scalars(select(FeatureRequests)).all()
        msg = "`"
        for item in features:
            feature: FeatureRequests = item
            msg = msg + str(feature.Id) + ". " + feature.Request + " - by " + feature.User + "\n"

        msg = msg + "`"
        await interaction.response.send_message(msg)

    @app_commands.command(name="roll", description="Test your luck for the day")
    async def roll(self, interaction: discord.Interaction):
        now = datetime.datetime.now()
        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>')
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>')
        today_date_str = now.strftime("%m/%d/%Y")
        seed = str(interaction.user.id) + today_date_str
        random.seed(seed)
        roll = random.randint(1, 100)
        is_lucky = roll >= 50
        
        print("Roll: " + str(roll))
        saving_throw = False

        try:
            if is_lucky is False:
                saving_throw_roll = random.randint(0,25)
                is_lucky = saving_throw_roll == 1 
                saving_throw = is_lucky

            overall_roller = BaseRollHelper(interaction.user, self.db, UserIdLuck)            
            monthly_roller = MonthlyRollHelper(interaction.user, self.db, UserIdMonthlyLuck)
            already_rolled = overall_roller.has_already_rolled(today_date_str)

            if already_rolled is False:
                overall_roller.process_roll(is_lucky, today_date_str)
                monthly_roller.process_roll(is_lucky, today_date_str)
                log = RollLogs()
                log.UserId = interaction.user.id
                log.RollDate = today_date_str
                log.WasLucky = is_lucky
                self.db.session.add(log)
                self.db.session.commit()
                
            overall_message = overall_roller.generate_result_message(lucky_var_emoji_message, unlucky_var_emoji_message, None)
            monthly_message = monthly_roller.generate_result_message()
            streak_display = overall_roller.user_row.CurrentLuckyStreak if is_lucky else overall_roller.user_row.CurrentUnluckyStreak
            the_view = RollResultView(lucky=is_lucky, 
                                    saving_throw=saving_throw,
                                    roll_totals_with_emojis=overall_message,
                                    roll_streak=streak_display,
                                    already_rolled=already_rolled
                                    )
            the_view.add_special_leaderboard_result(type=monthly_roller.get_month() + " Stats",message=monthly_message)
            the_view.add_author(interaction.user)
            
            await interaction.response.send_message(embed=the_view.get_embed(), view=the_view)


        except Exception: 
            print(traceback.format_exc())
            await interaction.response.send_message("roll is broken, will fix asap probably")

    @app_commands.command(name="react_count", description="See the number of messages that CowboyBot has reacted to")    
    @app_commands.describe(type = "See the most used cowboy word, the least used, or show the list of all cowboy words and their frequency")
    @app_commands.choices(type = [
        Choice(name = "All", value = "all"),
        Choice(name = "Most Used", value = "top"),
        Choice(name = "Least Used", value = "bottom")
    ])
    async def reactcount(self, interaction: discord.Interaction, type: str) -> None:
        react_rows = self.db.get_cowboy_reacts_count()
        total_react_count = len(self.db.get_cowboy_reacts())
        sorted_count_list = []
        for row in react_rows:
            entry = CowboyReact(row[0], row[1])
            sorted_count_list.append(entry)

        sorted_count_list.sort(key=lambda x: x.count, reverse=True)
        if len(sorted_count_list) == 0:
            await interaction.response.send_message("Could not obtain cowboy word list, sad yeehaw")
            return
        
        msg = ""

        if type == 'top':    
            top_entry = sorted_count_list[0]
            msg = "The top cowboy word is `" + top_entry.trigger_word + "`, occurring " + str(top_entry.count) + " times"
            await interaction.response.send_message(msg)
        elif type == 'bottom':
            bottom_entry = sorted_count_list[-1]
            msg = "The bottom cowboy word is `" + bottom_entry.trigger_word + "`, occurring " + str(bottom_entry.count) + " times"
            await interaction.response.send_message(msg)
        elif type == 'all':
            msg = "```\n"
            try:
                for index, item in enumerate(sorted_count_list):
                    msg = msg + str(index + 1) + '. ' + item.trigger_word + ', ' + str(item.count) + ' times\n'
                msg = msg + "\nTotal: " + str(total_react_count) + " times" + "\n```"
                await interaction.response.send_message(msg)
            except Exception as e:
                print(e)

    # This is basically just a dev command to test out random stuff
    @app_commands.command(name="sandbox", description="For dev testing whatever code is contained in this command")
    async def sandbox(self, interaction: discord.Interaction):
        if interaction.user.id != 350035723329470465:
            await interaction.response.send_message("u ain't allowed")
            return
        result = ":)"
        await interaction.response.send_message(result)
        return
    
    @app_commands.command(name="my_stats", description="Show your roll totals + current streak")
    @app_commands.describe(person = "View another person's stats instead")
    async def my_stats(self, interaction: discord.Interaction, person: discord.Member = None):
        user_to_lookup = interaction.user
        if (person is not None):
            user_to_lookup = person
        name_helper = NameHelper(user_to_lookup)
        user_name = name_helper.get_user_name()

        overall: UserIdLuck = self.db.session.scalars(select(UserIdLuck).where(UserIdLuck.UserId == user_to_lookup.id)).first()
        monthly: UserIdMonthlyLuck = self.db.session.scalars(select(UserIdMonthlyLuck).where(UserIdMonthlyLuck.UserId == user_to_lookup.id)).first()
        result = "Stats for " + user_name + ":\n\nOverall - lucky: `" + str(overall.LuckyCount) + "` / unlucky: `" + str(overall.UnluckyCount) + "`"
        result = result + "\nMonthly - lucky: `" + str(monthly.LuckyCount) + "` / unlucky: `" + str(monthly.UnluckyCount) + "`"
        if (overall.CurrentLuckyStreak > 0):
            result = result + "\n\nStreak - lucky streak of: `" + str(overall.CurrentLuckyStreak) + "`"
        elif (overall.CurrentUnluckyStreak > 0):
            result = result + "\n\nStreak - unlucky streak of: `" + str(overall.CurrentUnluckyStreak) + "`"

        current_month = datetime.datetime.now().month
        roll_logs: list[RollLogs] = list(self.db.session.scalars(select(RollLogs).where(RollLogs.UserId == user_to_lookup.id).order_by(RollLogs.Id)).all())
        if len(roll_logs) != 0:
            user_name = NameHelper(interaction.user).get_user_name()
            embeds: list[PageableEmbedItem] = []

            # overall roll history
            roll_log_graph_helper = RollLogImageHelper(user_name=user_name, logs=roll_logs)
            overall_graph_image = roll_log_graph_helper.generate_graph_image("Overall")
            overall_graph_embed = discord.Embed()
            overall_pageable_embed_item = PageableEmbedItem(overall_graph_embed, overall_graph_image)
            # build the discord image file since we'll start the pageable embed view on the first page, which is the overall one
            overall_pageable_embed_item_image_file = overall_pageable_embed_item.build_and_update_embed_image_file("result.png")
            embeds.append(overall_pageable_embed_item)

            # monthly roll history
            monthly_roll_logs = list(filter(lambda x: datetime.datetime.strptime(x.RollDate, "%m/%d/%Y").date().month == current_month, roll_logs))
            if len(monthly_roll_logs) > 0:
                monthly_roll_log_graph_helper = RollLogImageHelper(user_name=user_name, logs=monthly_roll_logs)
                monthly_graph_image = monthly_roll_log_graph_helper.generate_graph_image("Monthly")
                monthly_graph_embed = discord.Embed()
                monthly_pageable_embed_item = PageableEmbedItem(monthly_graph_embed, monthly_graph_image)
                # no need to build the discord image file - we'll build it when the pageable embed item is navigated to
                embeds.append(monthly_pageable_embed_item)

            view = PageableEmbedView(embeds=embeds, start_page=0)
            await interaction.response.send_message(content=result, embed=view.get_current_embed().get_embed(),view=view,file=overall_pageable_embed_item_image_file)
        else:
            await interaction.response.send_message(result)

            

async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        CommandCog(bot,db)
    )
        