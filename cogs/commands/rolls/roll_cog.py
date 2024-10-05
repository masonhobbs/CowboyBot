import datetime
import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.commands.helpers.rolls.monthly_roll_emoji_helper import MonthlyRollEmojiHelper
from db.db_handler import DbHandler
from cogs.commands.helpers.common.name_helper import NameHelper
from cogs.commands.helpers.rolls.roll_log_image_helper import RollLogImageHelper
from cogs.commands.helpers.rolls.leaderboard_helper import Leaderboard_Helper
from cogs.commands.helpers.rolls.base_roll_helper import BaseRollHelper
from cogs.commands.helpers.rolls.monthly_roll_helper import MonthlyRollHelper
from cogs.commands.ui.views.models.pageable_embed_item import PageableEmbedItem
from cogs.commands.ui.views.pageable_embed_view import PageableEmbedView
from cogs.commands.ui.views.roll_result_view import RollResultView
import traceback
from sqlalchemy import select
from db.tables.roll_logs import RollLogs
from db.tables.user_id_luck import UserIdLuck
from db.tables.user_id_monthly_luck import UserIdMonthlyLuck
from db.tables.roll_streak_record import RollStreakRecord

class RollCog(commands.Cog):
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db: DbHandler = db

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
        
        saving_throw = False
        saving_fail = False
        try:
            if is_lucky is False:
                saving_throw_roll = random.randint(0,25)
                is_lucky = saving_throw_roll == 1 
                saving_throw = is_lucky

            if is_lucky is True:
                saving_fail_roll = random.randint(0,35)
                saving_fail = saving_fail_roll == 1
                is_lucky = saving_fail is False

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
            monthly_emoji_helper = MonthlyRollEmojiHelper()
            streak_display = overall_roller.user_row.CurrentLuckyStreak if is_lucky else overall_roller.user_row.CurrentUnluckyStreak
            the_view = RollResultView(lucky=is_lucky, 
                                    saving_throw=saving_throw,
                                    saving_fail=saving_fail,
                                    roll_totals_with_emojis=overall_message,
                                    roll_streak=streak_display,
                                    already_rolled=already_rolled,
                                    lucky_emoji_override=monthly_emoji_helper.get_month_lucky_emoji(),
                                    unlucky_emoji_override=monthly_emoji_helper.get_month_unlucky_emoji()
                                    )
            the_view.add_special_leaderboard_result(type=monthly_roller.get_month(),message=monthly_message)
            the_view.add_author(interaction.user)
            
            await interaction.response.send_message(embed=the_view.get_embed(), view=the_view)


        except Exception: 
            print(traceback.format_exc())
            await interaction.response.send_message("roll is broken, will fix asap probably")

    @app_commands.command(name="my_stats", description="Show your roll totals + current streak")
    @app_commands.describe(person = "View another person's stats instead")
    async def my_stats(self, interaction: discord.Interaction, person: discord.Member = None):
        user_to_lookup = interaction.user if person is None else person
        name_helper = NameHelper(user_to_lookup)
        user_name = name_helper.get_user_name()
        specific_user_prefix = None if person is None else "Stats for **" + user_name + "**:\n\n"
        month_name = datetime.datetime.now().strftime("%B")
        lucky_var_emoji_message = str('<:alex_pogguhz:845468275332087868>')
        unlucky_var_emoji_message = str('<:peepoNuggie:747675590668058706>')
        monthly_emoji_helper = MonthlyRollEmojiHelper()
        current_month = datetime.datetime.now().month

        # query for current stat totals
        overall: UserIdLuck = self.db.session.scalars(select(UserIdLuck).where(UserIdLuck.UserId == user_to_lookup.id)).first()
        monthly: UserIdMonthlyLuck = self.db.session.scalars(select(UserIdMonthlyLuck).where(UserIdMonthlyLuck.UserId == user_to_lookup.id)).first()
        
        # build message text
        result = str("" if specific_user_prefix is None else specific_user_prefix) + "Overall - " + lucky_var_emoji_message + " `" + str(overall.LuckyCount) + "`  " + unlucky_var_emoji_message + " `" + str(overall.UnluckyCount) + "`\n"
        result = result + "\n" + str(month_name) + " - " + monthly_emoji_helper.get_month_lucky_emoji() + " `" + str(monthly.LuckyCount) + "`  " + monthly_emoji_helper.get_month_unlucky_emoji() + " `" + str(monthly.UnluckyCount) + "`\n"
        if (overall.CurrentLuckyStreak > 0):
            result = result + "\nLucky streak of: `" + str(overall.CurrentLuckyStreak) + "`"
        elif (overall.CurrentUnluckyStreak > 0):
            result = result + "\nUnlucky streak of: `" + str(overall.CurrentUnluckyStreak) + "`"

        # query for all logs of user
        roll_logs: list[RollLogs] = list(self.db.session.scalars(select(RollLogs).where(RollLogs.UserId == user_to_lookup.id).order_by(RollLogs.Id)).all())
        if len(roll_logs) != 0:
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
                monthly_graph_image = monthly_roll_log_graph_helper.generate_graph_image(month_name)
                monthly_graph_embed = discord.Embed()
                monthly_pageable_embed_item = PageableEmbedItem(monthly_graph_embed, monthly_graph_image)
                # no need to build the discord image file atm, we'll build it when the pageable embed item is navigated to
                embeds.append(monthly_pageable_embed_item)

            view = PageableEmbedView(embeds=embeds, start_page=0)
            await interaction.response.send_message(content=result, embed=view.get_current_embed().get_embed(),view=view,file=overall_pageable_embed_item_image_file)
        else:
            await interaction.response.send_message(result)

    @app_commands.command(name="all_stats", description="Show total lucky/unlucky graphs")
    async def all_stats(self, interaction: discord.Interaction):
        current_month = datetime.datetime.now().month
        roll_logs: list[RollLogs] = list(self.db.session.scalars(select(RollLogs).order_by(RollLogs.Id)).all())
        if len(roll_logs) != 0:
            embeds: list[PageableEmbedItem] = []

            # overall roll history
            roll_log_graph_helper = RollLogImageHelper(user_name="All Cowboys", logs=roll_logs)
            overall_graph_image = roll_log_graph_helper.generate_all_stats_graph_image("Overall")
            overall_graph_embed = discord.Embed()
            overall_pageable_embed_item = PageableEmbedItem(overall_graph_embed, overall_graph_image)
            
            # # build the discord image file since we'll start the pageable embed view on the first page, which is the overall one
            overall_pageable_embed_item_image_file = overall_pageable_embed_item.build_and_update_embed_image_file("result.png")
            embeds.append(overall_pageable_embed_item)

            # monthly roll history
            monthly_roll_logs = list(filter(lambda x: datetime.datetime.strptime(x.RollDate, "%m/%d/%Y").date().month == current_month, roll_logs))
            if len(monthly_roll_logs) > 0:
                monthly_roll_log_graph_helper = RollLogImageHelper(user_name="All Cowboys", logs=monthly_roll_logs)
                monthly_graph_image = monthly_roll_log_graph_helper.generate_all_stats_graph_image("Monthly")
                monthly_graph_embed = discord.Embed()
                monthly_pageable_embed_item = PageableEmbedItem(monthly_graph_embed, monthly_graph_image)
                # no need to build the discord image file - we'll build it when the pageable embed item is navigated to
                embeds.append(monthly_pageable_embed_item)

            view = PageableEmbedView(embeds=embeds, start_page=0)
            await interaction.response.send_message(content="Results", embed=view.get_current_embed().get_embed(),view=view,file=overall_pageable_embed_item_image_file)
        else:
            await interaction.response.send_message("Results")

            

async def setup(bot: commands.Bot) -> None:
    db = DbHandler()
    await bot.add_cog(
        RollCog(bot,db)
    )
        