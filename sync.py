# sync.py
# Cog for ?sync command
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

class SyncCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Add slash commands to server
    @commands.guild_only()
    @commands.command()
    async def sync(self, ctx):
        guild = ctx.guild
    
        await ctx.send('Slash commands ready!')

# Setup function
async def setup(client):
    await client.add_cog(SyncCog(client))