# trade.py
# Cog for ?trade command
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

# Variables to carry over from command function to button function
user_id = 0
target_id = 0
give_thing = ''
take_thing = ''
give_item_name = ''
take_item_name = ''
give_count = 0
take_count = 0
embed_trade_offer = discord.Embed(title='\u200b', description='', color=0xabcdef)

# Button function
class TradeButtons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Accept",style=discord.ButtonStyle.green)  # Button to accept trade offer
    async def green_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != target_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove the button instead of disabling it
        global embed_trade_offer
        await interaction.response.edit_message(embed=embed_trade_offer, view=None)

        # Check if target has enough items to trade
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        accept_valid = 0

        for i in range(len(lb)):
            if target_id == lb[i]['id']:
                for key, value in lb[i]['inventory'].items():
                    if take_thing.upper() == key.upper():
                        if value >= take_count:
                            lb[i]['inventory'][key] -= take_count  # Deduct take item from target inventory
                            accept_valid += 1
                            break
                
                break
        
        if accept_valid == 0:
            await interaction.channel.send('You do not have the item(s) you are trying to give!')
            return
        
        # Give take item to user
        for a in range(len(lb)):
            if user_id == lb[a]['id']:
                if take_item_name not in lb[a]['inventory']:
                    lb[a]['inventory'][take_item_name] = take_count
                else:
                    lb[a]['inventory'][take_item_name] += take_count
                break
        
        # Deduct give item from user inventory
        for b in range(len(lb)):
            if user_id == lb[b]['id']:
                for key_b, value_b in lb[b]['inventory'].items():
                    if give_thing.upper() == key_b.upper():
                        if value_b >= give_count:
                            lb[b]['inventory'][key_b] -= give_count
                            break
                
                break
        
        # Give give item to target
        for c in range(len(lb)):
            if target_id == lb[c]['id']:
                if give_item_name not in lb[c]['inventory']:
                    lb[c]['inventory'][give_item_name] = give_count
                else:
                    lb[c]['inventory'][give_item_name] += give_count
                break
        
        # Compose trade result embed
        user_ping = f'<@{user_id}>'
        target_ping = f'<@{target_id}>'
        trade_desc = f'{user_ping} traded with {target_ping}!'

        embed_trade_success = discord.Embed(title='Trade accepted!', description=trade_desc, color=0xabcdef)

        await interaction.channel.send(embed=embed_trade_success)

        # Remove item(s) from user's inventory if count is 0
        for key, value in list(lb[a]['inventory'].items()):
            if (key != 'Gold Ingot') and (key != 'Amethyst') and (value == 0):
                del lb[a]['inventory'][key]
        
        # Remove item(s) from target's inventory if count is 0
        for key, value in list(lb[i]['inventory'].items()):
            if (key != 'Gold Ingot') and (key != 'Amethyst') and (value == 0):
                del lb[i]['inventory'][key]

        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)
    
    @discord.ui.button(label="Reject",style=discord.ButtonStyle.red)  # Button to reject trade offer
    async def red_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id != target_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove the button instead of disabling it
        global embed_trade_offer
        await interaction.response.edit_message(embed=embed_trade_offer, view=None)

        await interaction.channel.send('Offer rejected!')

# ?trade command
class TradeCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.guild_only()
    @commands.command()
    async def trade(self, ctx, give_item='', give_amount=0, take_item='', take_amount=0, target=''):
        if target == '':  # empty string can't be sliced and turned into int
            await ctx.send('You must specify who to trade with!')
            return

        global give_thing  # Carry trade offer details to the button function
        global take_thing
        global give_count
        global take_count

        give_thing = give_item
        take_thing = take_item
        give_count = give_amount
        take_count = take_amount
        
        global user_id  # Carry the user and target IDs to the button function
        global target_id
        user_id = ctx.author.id

        target_id = target[2 : -1]
        if target_id.isdigit():
            target_id = int(target_id)
        else:
            await ctx.send('Invalid target username!')
            return

        if user_id == target_id:
            await ctx.send('Do you suck your own dick too?')
            return
        
        # Check if amounts are valid
        if (give_amount <= 0) or (take_amount <= 0):
            await ctx.invoke(self.client.get_command('succ'))
            return

        # Check if target exists
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        target_valid = 0
        for g in range(len(lb)):
            if target_id == lb[g]['id']:
                target_valid += 1
                break
        
        if target_valid == 0:
            await ctx.send('The person you want to trade with does not exist, or has nothing to give you!')
            return

        global give_item_name
        global take_item_name
        
        # Check if item to give exists
        exist = 0
        if exist == 0:
            for i in range(len(pl_items)):  # Check in normal items list
                if give_item.upper() == pl_items[i]['name'].upper():
                    give_item_type = 'Normal'
                    give_item_name = pl_items[i]['name']
                    give_item_emoji = pl_items[i]['emoji']
                    exist += 1
                    break
        
        if exist == 0:
            for a in range(len(recipe)):  # Check in crafted items recipe
                if give_item.upper() == recipe[a]['name'].upper():
                    give_item_type = 'Crafted'
                    give_item_name = recipe[a]['name']
                    give_item_emoji = recipe[a]['emoji']
                    exist += 1
                    break
        
        if exist == 0:
            for b in range(len(catalog)):  # Check in shop items catalog
                if give_item.upper() == catalog[b]['name'].upper():
                    give_item_type = 'Shop'
                    give_item_name = catalog[b]['name']
                    give_item_emoji = catalog[b]['emoji']
                    exist += 1
                    break
        
        if exist == 0:
            nonexist_item_string = f'Item `{give_item}` does not exist!'
            await ctx.send(nonexist_item_string)
            return
        
        # Check if item to take exists
        exist = 0
        if exist == 0:
            for c in range(len(pl_items)):  # Check in normal items list
                if take_item.upper() == pl_items[c]['name'].upper():
                    take_item_type = 'Normal'
                    take_item_name = pl_items[c]['name']
                    take_item_emoji = pl_items[c]['emoji']
                    exist += 1
                    break
        
        if exist == 0:
            for d in range(len(recipe)):  # Check in crafted items recipe
                if take_item.upper() == recipe[d]['name'].upper():
                    take_item_type = 'Crafted'
                    take_item_name = recipe[d]['name']
                    take_item_emoji = recipe[d]['emoji']
                    exist += 1
                    break
        
        if exist == 0:
            for e in range(len(catalog)):  # Check in shop items catalog
                if take_item.upper() == catalog[e]['name'].upper():
                    take_item_type = 'Shop'
                    take_item_name = catalog[e]['name']
                    take_item_emoji = catalog[e]['emoji']
                    exist += 1
                    break
        
        if exist == 0:
            nonexist_item_string = f'Item `{take_item}` does not exist!'
            await ctx.send(nonexist_item_string)
            return
        
        # Check if user has enough items to trade

        valid_offer = 0
        
        for f in range(len(lb)):
            if user_id == lb[f]['id']:
                for key, value in lb[f]['inventory'].items():
                    if key == give_item_name:
                        if value >= give_amount:
                            valid_offer += 1
                            break
                
                break
        
        if valid_offer == 0:
            await ctx.send('You do not have the item(s) you\'re offering!')
            return
        
        # Compose trade offer embed
        user_name = await self.client.fetch_user(user_id)
        user_name = user_name.name

        global embed_trade_offer
        embed_trade_offer.clear_fields()  # Reset embed from last offer

        embed_trade_offer.title = f'{user_name} sent a trade offer!'

        embed_trade_offer.add_field(name='With', value=target, inline=False)

        offer_field = f'{give_item_emoji} {give_item_name}: {give_amount}'
        embed_trade_offer.add_field(name='Their offer', value=offer_field, inline=True)

        take_field = f'{take_item_emoji} {take_item_name}: {take_amount}'
        embed_trade_offer.add_field(name='They will take', value=take_field, inline=True)

        await ctx.send(embed=embed_trade_offer, view=TradeButtons())

# Setup function
async def setup(client):
    await client.add_cog(TradeCog(client)) 