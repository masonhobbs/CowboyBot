import discord
from db.tables.roll_streak_record import RollStreakRecord

class Leaderboard_Helper():
    def build_leaderboard_embed(self,title,rows,color,streak_record: RollStreakRecord) -> discord.Embed:
        num_lucky_users = 0
        num_lucky_rolls = 0
        num_unlucky_users = 0
        num_unlucky_rolls = 0
        total_rolls = 0
            
        rows.sort(key=lambda x: x.LuckyCount, reverse=True)
        lucky_msg = self.build_lucky_message(rows)
        rows.sort(key=lambda x: x.UnluckyCount, reverse=True)
        unlucky_msg = self.build_unlucky_message(rows)
        for row in rows:
            total_rolls += row.UnluckyCount
            num_unlucky_rolls += row.UnluckyCount
            num_unlucky_users += 1
            total_rolls += row.LuckyCount
            num_lucky_rolls += row.LuckyCount
            num_lucky_users += 1

        average_lucky_percent = (float(num_lucky_rolls) / float(total_rolls))
        average_unlucky_percent = (float(num_unlucky_rolls) / float(total_rolls))
        formatted_lucky_percent = "{:.1%}".format(average_lucky_percent)
        formatted_unlucky_percent = "{:.1%}".format(average_unlucky_percent)
        embed_result = discord.Embed(title=title, color=color)
        embed_result.add_field(name="Lucker Dogs\t\t\t", value=lucky_msg, inline=True)
        embed_result.add_field(name="Bad Luck Brians", value=unlucky_msg, inline=True)
        embed_result.add_field(name="", value="", inline=False)
        embed_result.add_field(name="Total Rolls", value=str(total_rolls), inline=True)
        embed_result.add_field(name="Lucky Rolls %", value=str(formatted_lucky_percent),inline=True)
        embed_result.add_field(name="Unlucky Rolls %", value=str(formatted_unlucky_percent),inline=True)
        embed_result.add_field(name="", value="", inline=False)
        embed_result.add_field(name="Highest Lucky Streak", value=str(streak_record.HighestLuckyStreak), inline=True)
        embed_result.add_field(name="Highest Unlucky Streak", value=str(streak_record.HighestUnluckyStreak), inline=True)

        return embed_result
        
    def build_lucky_message(self,rows):
        result = ""
        for index, item in enumerate(rows):
            total = item.LuckyCount + item.UnluckyCount
            ratio = (float(item.LuckyCount) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            result = result + str (index + 1) + '. ' + item.Username + ' - ' + str(item.LuckyCount) + ' (' + str(formatted_ratio) + ')\t\t\n'

        return result

    def build_unlucky_message(self,rows):
        result = ""
        for index, item in enumerate(rows):
            total = item.LuckyCount + item.UnluckyCount
            ratio = (float(item.UnluckyCount) / float(total))
            formatted_ratio = "{:.1%}".format(ratio)
            result = result + str (index + 1) + '. ' + item.Username + ' - ' + str(item.UnluckyCount) + ' (' + str(formatted_ratio) + ')\t\t\n'

        return result
