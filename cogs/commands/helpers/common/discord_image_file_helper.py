import io
from PIL import Image
import discord

class DiscordImageFileHelper():
    def __init__(self, image: Image):
        self.image = image

    def build_file(self, filename: str) -> discord.File:
         with io.BytesIO() as image_binary:
            self.image.save(image_binary, 'PNG')
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename=filename)