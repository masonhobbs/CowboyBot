import discord
class LeaderboardSelection(discord.ui.View):
    options = [
        discord.SelectOption(label="Test1", value="1", description="Some test1"),
        discord.SelectOption(label="Test2", value="2", description="Some test2")
    ]

    @discord.ui.select(placeholder="Test test", options = options)  
    async def menu_callback(self, interaction: discord.Interaction, select):
        select.disabled = True
        print(select.values)
        print(select.values[0])

        # response = interaction.original_response
        # print(response)
        await interaction.response.edit_message(content="hello", view=LeaderboardSelection())
        return