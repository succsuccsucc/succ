# lenny.py
# Cog for ?lenny, ?misty, ?sunny, ?stairs commands
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

class LennyCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 1260, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def lenny(self, ctx):
        await ctx.send('https://tenor.com/view/dance-finn-adventure-time-lenny-face-gif-5268707')

    @commands.cooldown(1, 1440, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def misty(self, ctx):
        await ctx.send('https://tenor.com/view/phineas-and-ferb-dance-sing-moves-rap-gif-16504760')
    
    @commands.cooldown(1, 2220, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def sunny(self, ctx):
        await ctx.send('https://tenor.com/view/mao-gif-25413392')
    
    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def stairs(self, ctx):
        await ctx.send('https://tenor.com/view/fall-falling-pain-comedy-peter-griffin-gif-4624632')
    
async def setup(client):
    await client.add_cog(LennyCog(client))