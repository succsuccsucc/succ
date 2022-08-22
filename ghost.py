# ghost.py
# Cog for ?ghost and ?curse command
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

import pytz

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
    
    # Pass the curse to another user
    @commands.guild_only()
    @commands.command()
    async def curse(self, ctx, user=''):
        curse = open('data/cursed_user.json', 'r', encoding='utf-8')
        curse = json.load(curse)

        if ctx.author.id != curse[0]['id']:  # Only allow cursed user to curse others
            await ctx.send('Impostor! You are not the one who knocked.')
            return

        if len(curse) >= 4:
            await ctx.send('You already cursed someone!')
            return
        
        user_id = user[2 : -1]
        if not user_id.isdigit():
            await ctx.send('Invalid target!')
            return
        
        for i in range(len(curse)):
            if int(user_id) == curse[i]['id']:
                await ctx.send('Target already cursed in the last 2 days!')
                return

        # Add target to next entry in cursed_user.json
        new_curse = {"id": int(user_id),
                    "times": 0,
                    "date": str(datetime.date.today())
                    }
        
        curse.append(new_curse)
        
        # Send confirmation message
        author_ping = f'<@{ctx.author.id}>'
        await ctx.send(f'{author_ping} successfully cursed {user}!')

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
        today = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
        today = today.strftime('%Y-%m-%d')

        curse = open('data/cursed_user.json', 'r', encoding='utf-8')
        curse = json.load(curse)

        if today != curse[0]['date']:  # Pass curse to next user after each day
            if len(curse) == 4:
                curse[2] = curse[1]
                curse[1] = curse[0]
                curse[0] = curse[3]
                curse[0]['date'] = today

                del curse[3]

                old_curse_id = curse[1]['id']
                old_curse_ping = f'<@{old_curse_id}>'
                new_curse_id = curse[0]['id']
                new_curse_ping = f'<@{new_curse_id}>'

                general = await self.client.fetch_channel(981207955200426037)
                await general.send(f'A new day begins!\nThe curse has passed from {old_curse_ping} to {new_curse_ping}.')

                # Write changes
                outfile = open('data/cursed_user.json', 'w', encoding='utf-8')
                json.dump(curse, outfile, indent = 4)

# Setup function
async def setup(client):
    await client.add_cog(GhostCog(client))  