# inv.py
# Cog for ?inv command
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

from bot import pl_items, recipe, catalog

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# carry inventory embeds to the select menu function
embed_inv = None
embed_crafted_inv = None
embed_shop_inv = None
inv_description = None

class InvSelect(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label='All', emoji='🐈‍⬛'),
            discord.SelectOption(label='Normal', emoji='<:Lollipop:1003537715989598279>'),
            discord.SelectOption(label='Crafted', emoji='<:Amethyst:1004013520796520457>'),
            discord.SelectOption(label='Shop', emoji='<:Bath_Towel:1004352988074233886>')
            ]
        super().__init__(placeholder='Select type', max_values=1, min_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'All':
            embed_inv.description = inv_description
            embeds = [embed_inv, embed_crafted_inv, embed_shop_inv]
            await interaction.response.edit_message(content=None, embeds=embeds, view=None)
        elif self.values[0] == 'Normal':
            embed_inv.description = inv_description
            await interaction.response.edit_message(content=None, embed=embed_inv, view=None)
        elif self.values[0] == 'Crafted':
            embed_crafted_inv.description = inv_description
            await interaction.response.edit_message(content=None, embed=embed_crafted_inv, view=None)
        elif self.values[0] == 'Shop':
            embed_shop_inv.description = inv_description
            if len(embed_shop_inv) != (len(embed_shop_inv.title) + len(embed_shop_inv.description)):  # Only send if there are shop items in inventory
                await interaction.response.edit_message(content=None, embed=embed_shop_inv, view=None)
            else:
                await interaction.response.edit_message(content='User does not have any shop items!', embed=None, view=None)

class InvSelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(InvSelect())

class InvCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def inv(self, ctx, user=None):
        if not user:
            user_id = ctx.author.id
        else:
            user_id = user[2 : -1]

        user_name = await self.client.fetch_user(user_id)
        user_name = user_name.name

        global embed_inv
        global embed_crafted_inv
        global embed_shop_inv
        global inv_description
        
        inv_title = f'Inventory of {user_name}'
        
        embed_inv = discord.Embed(title=inv_title, description='', color=0xabcdef)

        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        # Display gold and amethyst count in description
        inv_description = ''
        
        for i in range(len(lb)):
            if int(user_id) == lb[i]['id']:

                if 'inventory' not in lb[i]:
                    break

                for c in range(len(pl_items)):
                    for key, value in lb[i]['inventory'].items():
                        item_name = key

                        if item_name == pl_items[c]['name']:
                            item_desc = pl_items[c]['description']
                            item_emoji = pl_items[c]['emoji']

                            # Add gold count to description string for display
                            if item_name == "Gold Ingot":
                                inv_description += item_emoji + ' ' + str(value)

                            item_field_title = item_emoji +' '+  item_name + ': ' + str(value)

                            embed_inv.add_field(name=item_field_title, value=item_desc, inline=False)
                            
                            break

                # Compose inventory of crafted items
                crafted_inv_title = f'Crafted items of {user_name}'

                embed_crafted_inv = discord.Embed(title=crafted_inv_title, description='', color=0xabcdef)

                for d in range(len(recipe)):
                    for key, value in lb[i]['inventory'].items():
                        thing_name = key

                        if thing_name == recipe[d]['name']:
                            thing_desc = recipe[d]['description']
                            thing_emoji = recipe[d]['emoji']

                            if thing_name == "Amethyst":
                                inv_description += ' | ' + thing_emoji + ' ' + str(value)

                            thing_field_title = thing_emoji + ' ' + thing_name + ': ' + str(value)

                            embed_crafted_inv.add_field(name=thing_field_title, value=thing_desc, inline=False)

                            break
                
                # Compose inventory of shop items
                shop_inv_title = f'Shop items of {user_name}'

                embed_shop_inv = discord.Embed(title=shop_inv_title, description='', color=0xabcdef)

                for e in range(len(catalog)):
                    for key_s, value_s in lb[i]['inventory'].items():
                        stuff_name = key_s

                        if stuff_name == catalog[e]['name']:
                            stuff_desc = catalog[e]['description']
                            stuff_emoji = catalog[e]['emoji']

                            stuff_field_title = stuff_emoji + ' ' + stuff_name + ': ' + str(value_s)

                            embed_shop_inv.add_field(name=stuff_field_title, value=stuff_desc, inline=False)

                            break

                await ctx.send('Please select inventory type:', view=InvSelectView())

                return
            
        await ctx.send('User does not have any items!')

# Setup function
async def setup(client):
    await client.add_cog(InvCog(client))   