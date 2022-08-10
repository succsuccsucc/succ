# help.py
# Cog for ?help command
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

class HelpCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def help(self, ctx, page=None):
        if not page:
            embed_help = discord.Embed(title='Help!', description='', color=0xcca6fd)

            embed_help.add_field(name='?succ', value='Consumes the last message in the channel.', inline=False)
            embed_help.add_field(name='?pointless', value='https://www.youtube.com/watch?v=EcSzq_6W1QQ', inline=False)
            embed_help.add_field(name='?test', value='Tests bot status.', inline=False)
            embed_help.add_field(name='?kmbtest <stop_name>', value='Tests if a bus stop with the given name exists.', inline=False)
            embed_help.add_field(name='?kmbeta <stop_name>', value='Gets ETA of all KMB routes at a bus stop.', inline=False)
            embed_help.add_field(name='?light <stop_name>', value='Gets train arrival times at a Light Rail stop.', inline=False)
            embed_help.add_field(name='?mtrfare <start> <end>', value='Gets the MTR fare between two stations.', inline=False)
            embed_help.add_field(name='?mtrbus <route>', value='Gets ETA at all bus stops of an MTR Bus route.', inline=False)

            command_count = str(len(embed_help.fields))
            footer_string = f'Total {command_count} commands in this page.\nUse "?help pointless" for commands about the pointless button.'
            embed_help.set_footer(text=footer_string)

            await ctx.send(embed=embed_help)

        if page == 'pointless':
            embed_help = discord.Embed(title='Help!', description='Commands about the pointless button', color=0xcca6fd)
            
            embed_help.add_field(name='?pointless', value='https://www.youtube.com/watch?v=EcSzq_6W1QQ', inline=False)
            embed_help.add_field(name='?leaderboard', value='Dick measuring contest.', inline=False)
            embed_help.add_field(name='?inv [page] [username]', value='Check a user\'s inventory.', inline=False)
            embed_help.add_field(name='?item <item>', value='Get info on an item.', inline=False)
            embed_help.add_field(name='?use <item> [target]', value='Use an item in your inventory.', inline=False)
            embed_help.add_field(name='?craft <item>', value='Craft items into another item.', inline=False)
            embed_help.add_field(name='?shop', value='Lists all items in the shop.', inline=False)
            embed_help.add_field(name='?buy <item> [amount]', value='Buy something from the shop.', inline=False)
            embed_help.add_field(name='?trade <give item> <amount> <take item> <amount> <target>', value='Trade items with someone.', inline=False)
            embed_help.add_field(name='?bet <bet>', value='Bet Gold Ingots that you can press the pointless button next! Bets go into a pool, which is given to the next person who presses the button.', inline=False)
            embed_help.add_field(name='?pool', value='View current bets in the bet pool.', inline=False)

            command_count=str(len(embed_help.fields))
            footer_string = f'Total {command_count} commands in this page.'
            embed_help.set_footer(text=footer_string)

            await ctx.send(embed=embed_help)

# Setup function
async def setup(client):
    await client.add_cog(HelpCog(client))   