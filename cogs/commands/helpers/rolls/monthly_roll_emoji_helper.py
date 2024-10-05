import datetime

class MonthlyRollEmojiHelper():
    def get_month_lucky_emoji(self) -> str:
        lucky_emoji = str('<:moyai_wine:1112926132883427450>')
        now = datetime.datetime.now()
        month = now.month
        if month == 2:
            lucky_emoji = ":black_heart:"
        if month == 9:
            lucky_emoji = ":statue_of_liberty:"
        if month == 10:
            lucky_emoji = ":jack_o_lantern:"
        if month == 11:
            lucky_emoji = ":turkey:"
        if month == 12:
            lucky_emoji = ":christmas_tree:"

        return lucky_emoji
    
    def get_month_unlucky_emoji(self) -> str:
        now = datetime.datetime.now()
        month = now.month
        unlucky_emoji = str('<:peepoHorror:754067746219753472>')
        if month == 2:
            unlucky_emoji = ":broken_heart:"
        if month == 9:
            unlucky_emoji = "✈️🏢🏢"
        if month == 10:
            unlucky_emoji = ":skull:"
        if month == 11:
            unlucky_emoji = ":fork_knife_plate:"
        if month == 12:
            unlucky_emoji = str('<:coal:1180190038550659082>')

        return unlucky_emoji