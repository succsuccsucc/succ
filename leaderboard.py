# leaderboard.py
# Cog for ?leaderboard command
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

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class LeaderboardCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def leaderboard(self, ctx):
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        name_list = []
        score_list = []
        rank_list = []
        
        for i in range(len(lb)):
            user_id = lb[i]['id']

            user_name = f'<@{user_id}>'
            name_list.append(user_name)

            score = lb[i]['score']
            score_list.append(str(score))

            rank_list.append(str(i + 1))

        if len(rank_list) >= 1:
            rank_list[0] = ':trophy: ' + rank_list[0]
        if len(rank_list) >= 2:
            rank_list[1] = ':second_place: ' + rank_list[1]
        if len(rank_list) >= 3:
            rank_list[2] = ':third_place: ' + rank_list[2]
        
        name_field = ''
        score_field = ''
        rank_field = ''
        
        name_field = '\n'.join(name_list)
        score_field = '\n'.join(score_list)
        rank_field = '\n'.join(rank_list)
        
        embed_leaderboard = discord.Embed(title='?pointless leaderboard', description='Get points by pressing the pointless button!', color=0xabcdef)

        embed_leaderboard.add_field(name='Rank', value=rank_field, inline=True)
        embed_leaderboard.add_field(name='Name', value=name_field, inline=True)
        embed_leaderboard.add_field(name='Score', value=score_field, inline=True)

        people_count = len(name_list)
        footer_leaderboard = f'Total {people_count} people.'
        embed_leaderboard.set_footer(text=footer_leaderboard)

        await ctx.send(embed=embed_leaderboard)

# Setup function
async def setup(client):
    await client.add_cog(LeaderboardCog(client))   