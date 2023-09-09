import discord
from typing import List

class PageableEmbedView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], start_page: int = 0):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.page = start_page
        self.max_pages = len(embeds)
        self.interaction: discord.Interaction = None
        self.back_button = BackButton(self.embeds)
        if (self.page == 0):
            self.back_button.disabled = True
        self.forward_button = ForwardButton(self.embeds)
        if (self.page == self.max_pages - 1):
            self.forward_button.disabled = True

        for index, embed in enumerate(self.embeds):
            embed.set_footer(text="Page " + str(index + 1) + " of " + str(self.max_pages))
        self.add_item(self.back_button)
        self.add_item(self.forward_button)
    

class ForwardButton(discord.ui.Button):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(label="Next",emoji="▶")
        self.embeds = embeds
        self.style = discord.ButtonStyle.primary
        self.view: PageableEmbedView
 

    async def callback(self, interaction: discord.Interaction):
        self.view.page += 1
        if self.view.page == self.view.max_pages - 1:
            self.view.forward_button.disabled = True
            self.view.back_button.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.view.page], view=self.view)
            

class BackButton(discord.ui.Button):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(label="Back",emoji="◀")
        self.embeds = embeds
        self.style = discord.ButtonStyle.secondary
        self.view: PageableEmbedView
 

    async def callback(self, interaction: discord.Interaction):
        self.view.page -= 1
        if self.view.page == 0:
            self.view.back_button.disabled = True
            self.view.forward_button.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.view.page], view=self.view)
            