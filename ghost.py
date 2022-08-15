# ghost.py
# Cog for ?ghost command
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

import config

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class GhostCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cursed_day.start()

    @commands.guild_only()
    @commands.command()
    async def ghost(self, ctx, pw=0):
        if pw != config.shush:
            await ctx.send('Impostor! You are not the one who knocked.')
            return

        curse = open('data/cursed_user.json', 'r', encoding='utf-8')
        curse = json.load(curse)
        
        cursed_user = await self.client.fetch_user(curse[0]['id'])

        if curse[0]['times'] >= 2:
            # await ctx.send(f'{cursed_user.name} has already been banned twice today!')
            print(f'{cursed_user.name} has already been banned twice today!')
            return
        
        if cursed_user.id == ctx.author.id:
            print(f'{cursed_user.name} just said it themselves!')
            return

        await ctx.send(f'{ctx.author} said it!\n{cursed_user.name} has been banned temporarily!')
        
        await ctx.guild.ban(cursed_user, reason='Boo!', delete_message_days=0)

        curse[0]['times'] += 1

        self.unban_loop.start(ctx.guild, ctx.channel, cursed_user)  # Start 15 minute countdown for unban

        # Write changes
        outfile = open('data/cursed_user.json', 'w', encoding='utf-8')
        json.dump(curse, outfile, indent = 4)
    
    @tasks.loop(seconds=5, count=2)
    async def unban_loop(self, guild, channel, cursed_user):
        if self.unban_loop.current_loop != 0:
            await guild.unban(cursed_user)
            await channel.send(f'{cursed_user.name} is now unbanned!')
    
    @tasks.loop(seconds=10.0)
    async def cursed_day(self):
        today = str(datetime.date.today())

        curse = open('data/cursed_user.json', 'r', encoding='utf-8')
        curse = json.load(curse)

        if today != curse[0]['date']:  # Reset ban count after each day
            curse[0]['times'] = 0
            curse[0]['date'] = today
        
            # Write changes
            outfile = open('data/cursed_user.json', 'w', encoding='utf-8')
            json.dump(curse, outfile, indent = 4)

# Setup function
async def setup(client):
    await client.add_cog(GhostCog(client))  