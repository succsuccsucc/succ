# ballstretcher.py
# Cog for ?ballstretcher command (bot only)
from http.client import HTTPException
import os
import ssl
import time
import requests
import datetime
import json
import csv
import random
import re
import asyncio

from collections import OrderedDict

import discord
from dotenv import load_dotenv

from discord.ext import commands
from discord.ext.commands import CommandNotFound

from bot import gold_emoji, amethyst_emoji
import config

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Open ball game scenarios file
games = open('data/pointless_ball_stretcher_games.json', encoding='utf-8')
games = json.load(games)

ball_user_id = 0  # Global variable to carry the command author to the button functions
ball_game_index = 0  # Carry the selected ball game to the buttons

# Ball game embed
embed_ball = discord.Embed(title='\u200b', description='', color=0xabcdef)
message = None  # Carry the embed to the button functions

class BallstretcherButton(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="A",style=discord.ButtonStyle.gray)
    async def a_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != ball_user_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove button after button is used
        global embed_ball
        await interaction.response.edit_message(embed=embed_ball, view=None)

        win_lose = random.randint(0, 3)  # Decide if user wins or loses (25% check)
        gold_amethyst = random.randint(0, 1)

        # Open user inventory
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        if gold_amethyst == 0:  # Choose between giving/taking gold and amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Gold Ingot'] += 30
                    else:  # Lose
                        if lb[i]['inventory']['Gold Ingot'] <= 10:
                            lb[i]['inventory']['Gold Ingot'] = 0
                        else:
                            lb[i]['inventory']['Gold Ingot'] -= 10
                    break
        
        else:  # Give/take amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Amethyst'] += 3
                    else:  # Lose
                        if lb[i]['inventory']['Amethyst'] <= 1:
                            lb[i]['inventory']['Amethyst'] = 0
                        else:
                            lb[i]['inventory']['Amethyst'] -= 1
                    break
        
        if win_lose == 0:  # Win
            embed_win = discord.Embed(title='Victory!', description=games[ball_game_index]['win']['A'], color=0x00ff00)

            if gold_amethyst == 0:
                win_field = f'{gold_emoji} 30'
            else:
                win_field = f'{amethyst_emoji} 3'

            embed_win.add_field(name='You won', value=win_field, inline=False)
            await interaction.channel.send(embed=embed_win)
        
        else:  # Lose
            embed_lose = discord.Embed(title='Defeat!', description=games[ball_game_index]['lose']['A'], color=0xff0000)

            if gold_amethyst == 0:
                lose_field = f'{gold_emoji} 10'
            else:
                lose_field = f'{amethyst_emoji} 1'

            embed_lose.add_field(name='You lost', value=lose_field, inline=False)
            await interaction.channel.send(embed=embed_lose)
        
        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)

    @discord.ui.button(label="B",style=discord.ButtonStyle.gray)
    async def b_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != ball_user_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove button after button is used
        global embed_ball
        await interaction.response.edit_message(embed=embed_ball, view=None)

        win_lose = random.randint(0, 3)  # Decide if user wins or loses (25% check)
        gold_amethyst = random.randint(0, 1)

        # Open user inventory
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        if gold_amethyst == 0:  # Choose between giving/taking gold and amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Gold Ingot'] += 30
                    else:  # Lose
                        if lb[i]['inventory']['Gold Ingot'] <= 10:
                            lb[i]['inventory']['Gold Ingot'] = 0
                        else:
                            lb[i]['inventory']['Gold Ingot'] -= 10
                    break
        
        else:  # Give/take amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Amethyst'] += 3
                    else:  # Lose
                        if lb[i]['inventory']['Amethyst'] <= 1:
                            lb[i]['inventory']['Amethyst'] = 0
                        else:
                            lb[i]['inventory']['Amethyst'] -= 1
                    break
        
        if win_lose == 0:  # Win
            embed_win = discord.Embed(title='Victory!', description=games[ball_game_index]['win']['B'], color=0x00ff00)

            if gold_amethyst == 0:
                win_field = f'{gold_emoji} 30'
            else:
                win_field = f'{amethyst_emoji} 3'

            embed_win.add_field(name='You won', value=win_field, inline=False)
            await interaction.channel.send(embed=embed_win)
        
        else:  # Lose
            embed_lose = discord.Embed(title='Defeat!', description=games[ball_game_index]['lose']['B'], color=0xff0000)

            if gold_amethyst == 0:
                lose_field = f'{gold_emoji} 10'
            else:
                lose_field = f'{amethyst_emoji} 1'

            embed_lose.add_field(name='You lost', value=lose_field, inline=False)
            await interaction.channel.send(embed=embed_lose)
        
        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)
    
    @discord.ui.button(label="C",style=discord.ButtonStyle.gray)
    async def c_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != ball_user_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove button after button is used
        global embed_ball
        await interaction.response.edit_message(embed=embed_ball, view=None)

        win_lose = random.randint(0, 3)  # Decide if user wins or loses (25% check)
        gold_amethyst = random.randint(0, 1)

        # Open user inventory
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        if gold_amethyst == 0:  # Choose between giving/taking gold and amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Gold Ingot'] += 30
                    else:  # Lose
                        if lb[i]['inventory']['Gold Ingot'] <= 10:
                            lb[i]['inventory']['Gold Ingot'] = 0
                        else:
                            lb[i]['inventory']['Gold Ingot'] -= 10
                    break
        
        else:  # Give/take amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Amethyst'] += 3
                    else:  # Lose
                        if lb[i]['inventory']['Amethyst'] <= 1:
                            lb[i]['inventory']['Amethyst'] = 0
                        else:
                            lb[i]['inventory']['Amethyst'] -= 1
                    break
        
        if win_lose == 0:  # Win
            embed_win = discord.Embed(title='Victory!', description=games[ball_game_index]['win']['C'], color=0x00ff00)

            if gold_amethyst == 0:
                win_field = f'{gold_emoji} 30'
            else:
                win_field = f'{amethyst_emoji} 3'

            embed_win.add_field(name='You won', value=win_field, inline=False)
            await interaction.channel.send(embed=embed_win)
        
        else:  # Lose
            embed_lose = discord.Embed(title='Defeat!', description=games[ball_game_index]['lose']['C'], color=0xff0000)

            if gold_amethyst == 0:
                lose_field = f'{gold_emoji} 10'
            else:
                lose_field = f'{amethyst_emoji} 1'

            embed_lose.add_field(name='You lost', value=lose_field, inline=False)
            await interaction.channel.send(embed=embed_lose)
        
        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)
    
    @discord.ui.button(label="D",style=discord.ButtonStyle.gray)
    async def d_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != ball_user_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove button after button is used
        global embed_ball
        await interaction.response.edit_message(embed=embed_ball, view=None)

        win_lose = random.randint(0, 3)  # Decide if user wins or loses (25% check)
        gold_amethyst = random.randint(0, 1)

        # Open user inventory
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        if gold_amethyst == 0:  # Choose between giving/taking gold and amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Gold Ingot'] += 30
                    else:  # Lose
                        if lb[i]['inventory']['Gold Ingot'] <= 10:
                            lb[i]['inventory']['Gold Ingot'] = 0
                        else:
                            lb[i]['inventory']['Gold Ingot'] -= 10
                    break
        
        else:  # Give/take amethyst
            for i in range(len(lb)):
                if lb[i]['id'] == ball_user_id:
                    if win_lose == 0:  # Win
                        lb[i]['inventory']['Amethyst'] += 3
                    else:  # Lose
                        if lb[i]['inventory']['Amethyst'] <= 1:
                            lb[i]['inventory']['Amethyst'] = 0
                        else:
                            lb[i]['inventory']['Amethyst'] -= 1
                    break
        
        if win_lose == 0:  # Win
            embed_win = discord.Embed(title='Victory!', description=games[ball_game_index]['win']['D'], color=0x00ff00)

            if gold_amethyst == 0:
                win_field = f'{gold_emoji} 30'
            else:
                win_field = f'{amethyst_emoji} 3'

            embed_win.add_field(name='You won', value=win_field, inline=False)
            await interaction.channel.send(embed=embed_win)
        
        else:  # Lose
            embed_lose = discord.Embed(title='Defeat!', description=games[ball_game_index]['lose']['D'], color=0xff0000)

            if gold_amethyst == 0:
                lose_field = f'{gold_emoji} 10'
            else:
                lose_field = f'{amethyst_emoji} 1'

            embed_lose.add_field(name='You lost', value=lose_field, inline=False)
            await interaction.channel.send(embed=embed_lose)
        
        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)

class BallstretcherCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.guild_only()
    @commands.command()
    async def ballstretcher(self, ctx, pw=0, user=0):
        if pw != config.shush:
            await ctx.send('Impostor! You are not the one who knocked.')
            return
        
        global ball_user_id
        ball_user_id = user
        
        global ball_game_index
        ball_game_index = random.randint(0, len(games) - 1)
        
        global embed_ball
        embed_ball.clear_fields()  # Reset embed for the next game

        embed_ball.title = games[ball_game_index]['name']
        embed_ball.description = games[ball_game_index]['description']
        embed_ball.set_image(url=games[ball_game_index]['image'])

        choice_string = ''
        for key, value in games[ball_game_index]['choices'].items():
            choice_string += f'{key}: {value}\n'
        embed_ball.add_field(name='Your choices', value=choice_string, inline=False)
        
        global message
        message = await ctx.send(embed=embed_ball, view=BallstretcherButton())
    
# Setup function
async def setup(client):
    await client.add_cog(BallstretcherCog(client))  