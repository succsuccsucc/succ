# craft.py
# Cog for ?craft command
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

from bot import recipe, pl_items, catalog

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class CraftCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def craft(self, ctx, item, amount=1):
        # Check if amount is <= 0
        if amount <= 0:
            await ctx.invoke(self.client.get_command('succ'))
            return

        # Check if amount is integer
        if not str(amount).isdigit():
            await ctx.send('Invalid amount!')
            return

        # Check if item exists
        # Check in crafted items recipe
        exist = 0
        for i in range(len(recipe)):
            if item.upper() == recipe[i]['name'].upper():
                product_index = i
                product_name = recipe[i]['name']
                exist += 1
                break

        if exist == 0:
            nonexist_item_string = f'Item `{item}` does not exist or is not craftable!'
            await ctx.send(nonexist_item_string)
            return

        # Open user inventory
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)
        
        user_id = ctx.author.id

        # Find user's entry in leaderboard
        for a in range(len(lb)):
            if lb[a]['id'] == user_id:
                user_index = a
                break

        # Check if user has enough ingredients
        enough_check = 0
        for p_key, p_value in recipe[product_index]['ingredients'].items():
            for i_key, i_value in lb[user_index]['inventory'].items():
                if i_key == p_key:
                    if i_value >= (p_value * amount):
                        lb[user_index]['inventory'][i_key] -= (p_value * amount)
                        enough_check += 1
                        break
                    else:
                        break

        # Give crafted item if have enough ingredients
        if enough_check == len(recipe[product_index]['ingredients']):
            if recipe[product_index]['name'] not in lb[user_index]['inventory']:
                lb[user_index]['inventory'][product_name] = amount
            else:
                lb[user_index]['inventory'][product_name] += amount  
        else:  # Send error message if not enough ingredients
            await ctx.send('You do not have the required ingredients!')
            return

        # Remove item(s) from user's inventory if count is 0
        for key, value in list(lb[user_index]['inventory'].items()):
            if (key != 'Gold Ingot') and (key != 'Amethyst') and (value == 0):
                del lb[user_index]['inventory'][key]
            
        # Send confirmation message
        craft_confirm_title = f'Successfully crafted {product_name}!'
        embed_craft_confirm = discord.Embed(title=craft_confirm_title, description='', color=0xabcdef)

        ingredient_field = ''
        for key_2, value_2 in recipe[product_index]['ingredients'].items():
            for b in range(len(pl_items)):
                if key_2 == pl_items[b]['name']:
                    ingredient_field += pl_items[b]['emoji'] + ' '
                    break
            
            for c in range(len(recipe)):
                if key_2 == recipe[c]['name']:
                    ingredient_field += recipe[c]['emoji'] + ' '
                    break
            
            for d in range(len(catalog)):
                if key_2 == catalog[d]['name']:
                    ingredient_field += catalog[d]['emoji'] + ' '
                    break

            ingredient_field += key_2 + ' x' + str(value_2 * amount) + '\n'
        
        embed_craft_confirm.add_field(name='Used', value=ingredient_field, inline=False)

        product_field = recipe[product_index]['emoji'] + ' ' + product_name + ' x' + str(amount)

        embed_craft_confirm.add_field(name='Crafted', value=product_field, inline=False)

        await ctx.send(embed=embed_craft_confirm)
        
        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)

# Setup function
async def setup(client):
    await client.add_cog(CraftCog(client))  
