import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from constants.cowboy_constants import CowboyConstants
import random
import time

class DuelCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="duel", description="Challenge an opponent to a western showdown")    
    @app_commands.describe(opponent = "The person you would like to duel")
    async def duel(self, interaction: discord.Interaction, opponent: discord.Member) -> None:
        duel_win_string = ""
        duel_win_string_start_time = None
        duel_loser_win_string_start_time = None
        duel_win_string_end_time = None
        duel_loser_win_string_end_time = None
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("You cannot duel yourself, pardner!")
            return
        if opponent.id == 723190104004493444:
            await interaction.response.send_message("You cannot duel me, pardner!")
            return
        
        await interaction.response.send_message('Yeehaw ' + opponent.mention + '!\n\n' + interaction.user.mention + ' has challenged you to duel! Do you accept? Reply "yes" or "no"!')
        try:
            def check_duel_acceptance(message: discord.Message):
                if message.author.id == opponent.id:
                    return message.content.lower() == "yes" or message.content.lower() == "no"
            
            def check_duel_answer(message: discord.Message):
                if message.author.id == interaction.user.id or message.author.id == opponent.id:
                    if message.content.lower() == duel_win_string:
                        return True

            opponent_response = await self.bot.wait_for('message', check=check_duel_acceptance, timeout=300)
            opponent_response.content = opponent_response.content.lower()
            if opponent_response.content == 'y' or opponent_response.content == 'yes':
                await interaction.followup.send(f"{interaction.user.mention} your duel has been accepted! The duel will take place in 20 seconds. The first person to send the cowboy phrase I send wins!");
                possible_options: int = len(CowboyConstants.cowboy_react_triggers)
                selected_options = []
                for i in range(0,3):
                    option = random.randint(0, possible_options - 1)
                    selected_options.append(CowboyConstants.cowboy_react_triggers[option])
                duel_win_string = ' '.join(selected_options)
                await asyncio.sleep(10)
                await interaction.followup.send(str('<:pausechamp:731010838248554507>') + ' incoming...')
                await asyncio.sleep(10)
                await interaction.followup.send(duel_win_string)

                try:                
                    duel_win_string_start_time = time.perf_counter() 
                    duel_loser_win_string_start_time = time.perf_counter()
                    winning_message = await self.bot.wait_for('message', check=check_duel_answer, timeout=60)
                    winner_id = winning_message.author.id
                    duel_win_string_end_time = time.perf_counter()
                    duel_win_time_seconds = f'Winning message was sent in {duel_win_string_end_time - duel_win_string_start_time:0.2f} seconds'

                    try:
                        await self.bot.wait_for('message', check=check_duel_answer, timeout=2)
                        duel_loser_win_string_end_time = time.perf_counter()
                        duel_loser_win_string_seconds = f'Losing message was sent in {duel_loser_win_string_end_time - duel_loser_win_string_start_time:0.2f} seconds'
                        if winner_id == interaction.user.id:
                            await interaction.followup.send(f"{interaction.user.mention} has won the duel! :cowboy: \n\n{opponent.mention} owned\n\n{duel_win_time_seconds}\n{duel_loser_win_string_seconds}")
                        elif winner_id == opponent.id:
                            await interaction.followup.send(f"{opponent.mention} has won the duel! :cowboy: \n\n{interaction.user.mention} owned\n\n{duel_win_time_seconds}\n{duel_loser_win_string_seconds}")
                    except:
                        if winner_id == interaction.user.id:
                            await interaction.followup.send(f"{interaction.user.mention} has won the duel! :cowboy: \n\n{opponent.mention} owned\n\n{duel_win_time_seconds}")
                        elif winner_id == opponent.id:
                            await interaction.followup.send(f"{opponent.mention} has won the duel! :cowboy: \n\n{interaction.user.mention} owned\n\n{duel_win_time_seconds}")
                except:
                    await interaction.followup.send("Neither challenger responded in time! The duel has been canceled.")

                
            elif opponent_response.content == 'n' or opponent_response.content == 'no':
                await interaction.followup.send(f"Coward! {interaction.user.mention} your opponent has declined!")
            else: 
                await interaction.followup.send('You did not reply "yes" or "no"! The duel has been canceled.')
        except:
            await interaction.followup.send(f"{interaction.user.mention}, the opponent did not respond in time!")
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        DuelCog(bot)
    )
        