from typing import Union

import discord

class NameHelper():
    def __init__(self, discord_user: Union[discord.User, discord.Member]):
        self.user = discord_user

    def get_user_name(self) -> str:
        result = ""
        if hasattr(self.user, "nick") and self.user.nick is not None and len(self.user.nick) > 0:
            result = self.user.nick
        elif hasattr(self.user, "global_name") and self.user.global_name is not None and len(self.user.global_name) > 0:
            result = self.user.global_name
        elif hasattr(self.user, "display_name") and self.user.display_name is not None and len(self.user.display_name) > 0:
            result = self.user.display_name
        else:
            result = self.user.name

        return result