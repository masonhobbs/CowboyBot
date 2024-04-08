import discord
from PIL import Image

from cogs.commands.helpers.common.discord_image_file_helper import DiscordImageFileHelper

class PageableEmbedItem():
    def __init__(self, embed: discord.Embed, image: Image = None):
        self.__embed: discord.Embed = embed
        self.__image_file_builder = None

        if (image is not None):
            self.__image_file_builder: DiscordImageFileHelper = DiscordImageFileHelper(image)
        else:
            return

    def build_and_update_embed_image_file(self, filename: str) -> discord.File:
        if (self.__image_file_builder is not None):
            self.__embed.set_image(url="attachment://" + filename)
            return self.__image_file_builder.build_file(filename)
        return None

    def has_image(self) -> bool:
        return self.__image_file_builder is not None

    def update_footer(self, footer: str):
        self.__embed.set_footer(text=footer)

    def get_embed(self):
        return self.__embed

