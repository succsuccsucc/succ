# shop.py
# Cog for ?shop command
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

from bot import catalog, gold_emoji, amethyst_emoji

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class ShopCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Display shop catalog
    @commands.guild_only()
    @commands.command()
    async def shop(self, ctx):
        # Read shop catalog
        embed_shop = discord.Embed(title='Shop', description='It\'s time to consume.', color=0xabcdef)
        
        # Display each item in catalog
        for i in range(len(catalog)):
            field_name = ''
            field_value = ''

            field_name += catalog[i]['emoji'] + ' ' +  catalog[i]['name'] + ': '

            if catalog[i]['currency'] == 'G':
                field_name += gold_emoji
            else:
                field_name += amethyst_emoji
            
            field_name += ' ' + str(catalog[i]['price'])

            field_value += catalog[i]['description']

            embed_shop.add_field(name=field_name, value=field_value, inline=False)
        
        # Show user currency balance in footer
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        user_id = ctx.author.id
        user_gold = 0
        user_amethyst = 0
        
        for a in range(len(lb)):
            if lb[a]['id'] == user_id:
                for key, value in lb[a]['inventory'].items():
                    if key == 'Gold Ingot':
                        user_gold = value
                    elif key == 'Amethyst':
                        user_amethyst = value

                break
                        
        you_have = gold_emoji + ' ' + str(user_gold) + ' | ' + amethyst_emoji + ' ' + str(user_amethyst)
        embed_shop.add_field(name='\u200b', value=you_have, inline=False)

        shop_footer = 'Use "?buy <item>" to buy an item, or learn more.'
        embed_shop.set_footer(text=shop_footer)

        await ctx.send(embed=embed_shop)
    
# Setup function
async def setup(client):
    await client.add_cog(ShopCog(client))  