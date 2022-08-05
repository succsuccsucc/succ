# item.py
# Cog for ?item command
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

from bot import pl_items, recipe, catalog, gold_emoji, amethyst_emoji

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class ItemCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Get info on an item
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    @commands.guild_only()
    async def item(self, ctx, item):
        # Check if item exists
        # Check in normal items list
        exist = 0
        for i in range(len(pl_items)):
            if item.upper() == pl_items[i]['name'].upper():
                item_type = 'Normal'
                exist += 1
                break
        
        # Check in crafted items recipe
        for a in range(len(recipe)):
            if item.upper() == recipe[a]['name'].upper():
                item_type = 'Crafted'
                exist += 1
                break
        
        # Check in shop items catalog
        for b in range(len(catalog)):
            if item.upper() == catalog[b]['name'].upper():
                item_type = 'Shop'
                exist += 1
                break

        if exist == 0:
            nonexist_item_string = f'Item `{item}` does not exist!'
            
            if len(nonexist_item_string) > 1024:
                await ctx.send('Bot response too long! Check your command.')
                return
            await ctx.send(nonexist_item_string)
            return
        
        # Display item info
        if item_type == 'Normal':
            item_name = pl_items[i]['name']
            item_flavor = pl_items[i]['description']
            item_desc = pl_items[i]['detail']
            item_emoji = pl_items[i]['emoji']

        elif item_type == 'Crafted':
            item_name = recipe[a]['name']
            item_flavor = recipe[a]['description']
            item_desc = recipe[a]['detail']
            item_emoji = recipe[a]['emoji']

        elif item_type == 'Shop':
            item_name = catalog[b]['name']
            item_flavor = catalog[b]['description']
            item_desc = catalog[b]['detail']
            item_emoji = catalog[b]['emoji']
        
        # Get emoji id and url from raw string
        emoji_id = re.findall('\d+', item_emoji)[0]

        if item_emoji[1] == 'a':
            emoji_url = 'https://cdn.discordapp.com/emojis/' + str(emoji_id) + '.gif'
        else:
            emoji_url = 'https://cdn.discordapp.com/emojis/' + str(emoji_id) + '.png'

        # Compose the embed
        embed_item = discord.Embed(title=item_name, description=item_flavor, color=0xabcdef)

        embed_item.set_thumbnail(url=emoji_url)

        embed_item.add_field(name='Description', value=item_desc, inline=False)
        embed_item.add_field(name='Type', value=item_type, inline=True)
        
        if item_type == 'Crafted':  # Get crafting ingredients of crafted item
            ingredient_field = ''
            for key, value in recipe[a]['ingredients'].items():
                for c in range(len(pl_items)):
                    if key == pl_items[c]['name']:
                        ingredient_field += pl_items[c]['emoji'] + ' ' + pl_items[c]['name'] + ': ' + str(value) + '\n'
                        break
            
            embed_item.add_field(name='Ingredients', value=ingredient_field, inline=True)
        
        elif item_type == 'Shop':  # Get price of shop item
            if catalog[b]['currency'] == 'G':
                shop_field = gold_emoji + ' ' + str(catalog[b]['price'])
            elif catalog[b]['currency'] == 'A':
                shop_field = amethyst_emoji + ' ' + str(catalog[b]['price'])
            
            embed_item.add_field(name='Price', value=shop_field, inline=True)
        
        await ctx.send(embed=embed_item)

# Setup function
async def setup(client):
    await client.add_cog(ItemCog(client))  