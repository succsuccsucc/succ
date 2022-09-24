# lenny.py
# Cog for ?lenny command
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
        lenny_list = ['(∩ ͡° ͜ʖ ͡°)⊃━☆ﾟ. * ･ ｡ﾟ,', '( ͡° ͜ʖ ͡°)╭∩╮']
        lenny_send = random.choice(lenny_list)
        await ctx.send(lenny_send)
    
async def setup(client):
    await client.add_cog(LennyCog(client))