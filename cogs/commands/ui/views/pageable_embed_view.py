import discord

from cogs.commands.helpers.common.discord_image_file_helper import DiscordImageFileHelper
from cogs.commands.ui.views.models.pageable_embed_item import PageableEmbedItem

class PageableEmbedView(discord.ui.View):
    def __init__(self, embeds: list[PageableEmbedItem], start_page: int = 0):
        super().__init__(timeout=None)
        self.__embeds = embeds
        self.page = start_page
        self.max_pages = len(embeds)
        self.interaction: discord.Interaction = None
        self.back_button = BackButton()
        
        if (self.page == 0):
            self.back_button.disabled = True
        self.forward_button = ForwardButton()
        if (self.page == self.max_pages - 1):
            self.forward_button.disabled = True

        page_display_number = 0
        for embed_item in self.__embeds:
            embed_item.update_footer(footer="Page " + str(page_display_number + 1) + " of " + str(self.max_pages))
            page_display_number += 1

        self.add_item(self.back_button)
        self.add_item(self.forward_button)

    def get_current_embed(self) -> PageableEmbedItem:
        return self.__embeds[self.page]
    
    async def update_message(self, interaction: discord.Interaction):
        if self.get_current_embed().has_image():
            embed_image_discord_file = self.get_current_embed().build_and_update_embed_image_file("result.png")
            await interaction.response.edit_message(embed=self.get_current_embed().get_embed(), view=self, attachments=[embed_image_discord_file])
        else:
            await interaction.response.edit_message(embed=self.get_current_embed().get_embed(), view=self)
    
class ForwardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next",emoji="▶")
        self.style = discord.ButtonStyle.primary
        self.view: PageableEmbedView
 

    async def callback(self, interaction: discord.Interaction):
        self.view.page += 1
        if self.view.page == self.view.max_pages - 1:
            self.view.forward_button.disabled = True
            self.view.back_button.disabled = False
        
        await self.view.update_message(interaction)

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back",emoji="◀")
        self.style = discord.ButtonStyle.secondary
        self.view: PageableEmbedView
 

    async def callback(self, interaction: discord.Interaction):
        self.view.page -= 1
        if self.view.page == 0:
            self.view.back_button.disabled = True
            self.view.forward_button.disabled = False

        await self.view.update_message(interaction)
            