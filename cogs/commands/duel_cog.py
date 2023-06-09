import discord
from discord.ext import commands
from discord import app_commands
import sys
import asyncio
from constants.cowboy_constants import CowboyConstants
import random
import datetime

class DuelCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="duel", description="Challenge an opponent to a western showdown")    
    @app_commands.describe(opponent = "The person you would like to duel")
    async def duel(self, interaction: discord.Interaction, opponent: discord.Member) -> None:
        duel_win_string = ""
        await interaction.response.send_message('Yeehaw ' + opponent.mention + '! ' + interaction.user.name + ' has challenged you to duel! Do you accept? Reply "yes" or "no"!')
        try:
            def check_duel_acceptance(message: discord.Message):
                if message.author.name != opponent.name:
                    return
                return message.author.name == opponent.name
            
            def check_duel_answer(message: discord.Message):
                if message.author.id == interaction.user.id or message.author.id == opponent.id:
                    if message.content.lower() == duel_win_string:
                        return True

            opponent_response = await self.bot.wait_for('message', check=check_duel_acceptance, timeout=300)
            opponent_response.content = opponent_response.content.lower()
            if opponent_response.content == 'y' or opponent_response.content == 'yes':
                await interaction.followup.send(f"{interaction.user.mention} your duel has been accepted! The duel will take place in 20 seconds. The first person to type out the cowboy phrase I send when the duel starts wins.");
                possible_options: int = len(CowboyConstants.cowboy_react_triggers)
                selected_options = []
                for i in range(0,3):
                    option = random.randint(0, possible_options - 1)
                    selected_options.append(CowboyConstants.cowboy_react_triggers[option])
                duel_win_string = ' '.join(selected_options)
                await asyncio.sleep(20)
                await interaction.followup.send(duel_win_string)

                try:                
                    challenger_wins = await self.bot.wait_for('message', check=check_duel_answer, timeout=60)
                    winner_id = challenger_wins.author.id
                    if winner_id == interaction.user.id:
                        await interaction.followup.send(f"{interaction.user.mention} has won the duel! :cowboy: \n\n{opponent.mention}" + str("<:pensivecowboy:834848610788835358>"))
                    elif winner_id == opponent.id:
                        await interaction.followup.send(f"{opponent.mention} has won the duel! :cowboy: \n\n{interaction.user.mention} " + str("<:pensivecowboy:834848610788835358>"))
                except:
                    await interaction.followup.send("Neither challenger responded in time! The duel has been canceled.")
                
            elif opponent_response.content == 'n' or opponent_response.content == 'no':
                await interaction.followup.send(f"Coward! {interaction.user.mention} your opponent has declined!")
        except:
            await interaction.followup.send(f"{interaction.user.mention}, the opponent did not respond in time!")
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        DuelCog(bot)
    )
        