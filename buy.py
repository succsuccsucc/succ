# buy.py
# Cog for ?buy command
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

# The following code handles buying things in the shop
buy_author_id = 0  # Global variable to carry the command author to interaction function
thing_name = ''  # Carry the item to buy
buy_amount = 0  # Carry the amount of items to buy
buy_currency = ''  # Carry the type of currency to pay
total_price = 0  # Carry the price to pay

thing_emoji = ''  # Carry the emoji of the item to buy

# Carry the item information embed
embed_buy = discord.Embed(title='\u200b', description='', color=0xabcdef)

# Buy an item
class BuyButton(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Buy",style=discord.ButtonStyle.blurple)
    async def blurple_button(self,interaction:discord.Interaction,button:discord.ui.Button):  
        if interaction.user.id != buy_author_id:
            await interaction.response.send_message(content='Impostor! You are not the one who knocked.', ephemeral=True)
            return
        
        # Remove the button instead of disabling it
        global embed_buy
        await interaction.response.edit_message(embed=embed_buy, view=None)

        # Reset the embed after item display finish
        embed_buy.clear_fields()

        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        # Check if user has enough balance
        # If enough, deduct the balance
        valid_balance = 0
        for a in range(len(lb)):
            if lb[a]['id'] == interaction.user.id:
                for key,value in lb[a]['inventory'].items():
                    if buy_currency == "G":
                        if (key == 'Gold Ingot') and (value >= total_price):
                            lb[a]['inventory'][key] -= total_price
                            valid_balance += 1
                            break
                    
                    elif buy_currency == "A":
                        if (key == 'Amethyst') and (value >= total_price):
                            lb[a]['inventory'][key] -= total_price
                            valid_balance += 1
                            break
                
                if (valid_balance == 0) and (buy_currency == "G"):
                    await interaction.channel.send('You do not have enough Gold Ingots!')
                    return
                elif (valid_balance == 0) and (buy_currency == "A"):
                    await interaction.channel.send('You do not have enough Amethyst!')
                    return
                
                break
        
        # Payment successful, give item(s) to user
        if thing_name not in lb[a]['inventory']:
            lb[a]['inventory'][thing_name] = buy_amount
        else:
            lb[a]['inventory'][thing_name] += buy_amount
        
        # Remove item(s) from user's inventory if count is 0
        for key_r, value_r in list(lb[a]['inventory'].items()):
            if (key_r != 'Gold Ingot') and (key_r != 'Amethyst') and (value_r == 0):
                del lb[a]['inventory'][key_r]

        # Send confirmation message
        if len(embed_buy_confirm) > 1024:
            await interaction.channel.send('Bot response too long! Check your command.')
            return
        embed_buy_confirm = discord.Embed(title='Deal!', description='', color=0xabcdef)

        buy_confirm_bought = f'{thing_emoji} {thing_name} x{buy_amount}'
        embed_buy_confirm.add_field(name='Bought', value=buy_confirm_bought, inline=True)

        if buy_currency == "G":
            buy_confirm_paid = f'{gold_emoji} {total_price}'
        elif buy_currency == "A":
            buy_confirm_paid = f'{amethyst_emoji} {total_price}'
        embed_buy_confirm.add_field(name='Paid', value=buy_confirm_paid, inline=True)

        for b in range(len(lb)):
            if lb[b]['id'] == interaction.user.id:
                for key_n, value_n in lb[b]['inventory'].items():
                    if key_n == 'Gold Ingot':
                        new_gold = value_n
                    elif key_n == 'Amethyst':
                        new_amethyst = value_n
        
        buy_confirm_balance = f'{gold_emoji} {new_gold} | {amethyst_emoji} {new_amethyst}'
        embed_buy_confirm.add_field(name='Balance', value=buy_confirm_balance, inline=False)

        if len(embed_buy_confirm) > 1024:
            await interaction.channel.send('Bot response too long! Check your command.')
            return
        await interaction.channel.send(embed=embed_buy_confirm)

        # Write changes to leaderboard
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)

class BuyCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.guild_only()
    @commands.command()
    async def buy(self, ctx, item, amount=1):
        # Reset embed from last use
        global embed_buy  # Carry the item information display
        embed_buy.clear_fields()

        global buy_author_id
        buy_author_id = ctx.author.id

        global thing_name  # Carry the item to buy

        # Check if purchase amount is valid
        if amount <= 0:
            await ctx.invoke(self.client.get_command('succ'))
            return

        # Check if item exists in shop
        exists_shop = 0
        for i in range(len(catalog)):
            if item.upper() == catalog[i]['name'].upper():
                thing_name = catalog[i]['name']
                exists_shop += 1
                break

        if exists_shop == 0:
            await ctx.send('We don\'t have that in the shop!')
            return
        
        # Display item information
        global thing_emoji 
        thing_emoji = catalog[i]['emoji']  # Carry the emoji of the item to buy

        # Get emoji id and url from raw string
        thing_emoji_id = re.findall('\d+', thing_emoji)[0]

        if thing_emoji[1] == 'a':
            thing_emoji_link = 'https://cdn.discordapp.com/emojis/' + str(thing_emoji_id) + '.gif'
        else:
            thing_emoji_link = 'https://cdn.discordapp.com/emojis/' + str(thing_emoji_id) + '.png'

        thing_flavor = catalog[i]['description']
        thing_desc = catalog[i]['detail']

        global buy_currency  # Carry the currency type to interaction function for checkout
        buy_currency = catalog[i]['currency']

        global buy_amount  # Carry the amount of items to buy
        buy_amount = amount

        embed_buy.title = f'You\'re about to buy: {thing_name}'
        embed_buy.description=thing_flavor

        embed_buy.set_thumbnail(url=thing_emoji_link)

        embed_buy.add_field(name='Description', value=thing_desc, inline=False)

        # Calculate price
        if catalog[i]['currency'] == "G":
            thing_price = gold_emoji + ' ' + str(catalog[i]['price'])
        if catalog[i]['currency'] == "A":
            thing_price = amethyst_emoji + ' ' + str(catalog[i]['price'])
        
        global total_price  # Carry the total price
        total_price = catalog[i]['price'] * amount

        if catalog[i]['currency'] == "G":
            total_price_display = gold_emoji + ' ' + str(catalog[i]['price'] * amount)
        if catalog[i]['currency'] == "A":
            total_price_display = amethyst_emoji + ' ' + str(catalog[i]['price'] * amount)
        
        embed_buy.add_field(name='Unit Price', value=thing_price, inline=True)
        embed_buy.add_field(name='Amount', value=amount, inline=True)
        embed_buy.add_field(name='Total Price', value=total_price_display, inline=True)

        if len(embed_buy) > 1024:
            await ctx.send('Bot response too long! Check your command.')
            return
        await ctx.send(embed=embed_buy, view=BuyButton())

# Setup function
async def setup(client):
    await client.add_cog(BuyCog(client)) 