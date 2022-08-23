# morb.py
# Cog for ?morb command (bot only)
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

from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

from bot import gold_emoji, amethyst_emoji
import config

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

morb_count = 0  # Carry the number of morb button clicks to the timeout loop
morb_user_id = 0  # Carry the item user to the button function

embed_morb = discord.Embed(title='\u200b', description='', color=0xabcdef)
message = None  # Carry the message to button and timeout function

class MorbButton(discord.ui.View):
    def __init__(self, *, timeout=10):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="Morb",style=discord.ButtonStyle.green)
    async def morb_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != morb_user_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        global morb_count
        morb_count += 1

        await interaction.response.edit_message(embed=embed_morb, view=MorbButton())
    
class MorbCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.guild_only()
    @commands.command()
    async def morb(self, ctx, pw=0, user=0):
        if pw != config.shush:
            await ctx.send('Impostor! You are not the one who knocked.')
            return
        
        # Reset morb count for new morb
        global morb_count
        morb_count = 0
        
        global morb_user_id
        morb_user_id = user  # carry the item user

        # send morb button
        global embed_morb
        global message
        embed_morb.clear_fields()  # Reset embed for next morb
        embed_morb.title = 'It\'s morbin time!'
        embed_morb.description = 'Mash the MORB BUTTON to morb!'
        embed_morb.set_image(url='https://cdn.discordapp.com/attachments/805744932975280158/1011650783730733166/unknown.png')

        message = await ctx.send(embed=embed_morb, view=MorbButton())

        # Start 10s morb countdown
        self.timeout.start()
    
    @tasks.loop(seconds=10.0, count=2)
    async def timeout(self):
        if self.timeout.current_loop != 0:     
            global message  # edit morb message to remove morb button and show morb result
            global morb_count

            if morb_count < 7:
                fail_string = f'Morb failed!\nYou lost {gold_emoji} 7.'
                await message.edit(content=fail_string, embed=None, view=None)

                # Open user inventory
                lb_file = open('data/pointless_leaderboard.json', 'r')
                lb = json.load(lb_file)

                for i in range(len(lb)):
                    if lb[i]['id'] == morb_user_id:
                        if lb[i]['inventory']['Gold Ingot'] <= 7:
                            lb[i]['inventory']['Gold Ingot'] == 0
                        else:
                            lb[i]['inventory']['Gold Ingot'] -= 7
                        break
            
            elif morb_count >= 7:
                success_string = f'Morb success!\nYou won {gold_emoji} 7.'
                await message.edit(content=success_string, embed=None, view=None)

                # Open user inventory
                lb_file = open('data/pointless_leaderboard.json', 'r')
                lb = json.load(lb_file)

                for a in range(len(lb)):
                    if lb[a]['id'] == morb_user_id:
                        lb[a]['inventory']['Gold Ingot'] += 7
                        break
            
            # Write changes to leaderboard
            outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
            json.dump(lb, outfile, indent = 4)

            # Reset morb count for next morb
            morb_count = 0

# Setup function
async def setup(client):
    await client.add_cog(MorbCog(client))