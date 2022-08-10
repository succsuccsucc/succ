# bet_pool.py
# Cog for ?bet and ?pool commands
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

from bot import gold_emoji

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class BetCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.guild_only()
    @commands.command()
    async def bet(self, ctx, amount=0):
        # Open bet pool file
        bet_pool = open('data/pointless_bet_pool.json', 'r', encoding='utf-8')
        bet_pool = json.load(bet_pool)

        # Check if bet is 0 or less
        if amount <= 0:
            await ctx.invoke(self.client.get_command('succ'))
            return
        
        # Check if bet is specified
        if not amount:
            await ctx.send('You must specify the bet!')
            return
        
        # Check if user already made a bet
        for a in range(len(bet_pool)):
            if ctx.author.id == bet_pool[a]['id']:
                await ctx.send('You already made a bet!')
                return
        
        # Check if bet is integer
        if not str(amount).isdigit():
            await ctx.send('Invalid bet!')
            return
        
        # Open leaderboard file
        lb_file = open('data/pointless_leaderboard.json', 'r')
        lb = json.load(lb_file)

        # Check if user has enough gold for bet
        bet_valid = 0
        for i in range(len(lb)):
            if lb[i]['id'] == ctx.author.id:
                for key,value in lb[i]['inventory'].items():
                    if (key == 'Gold Ingot') and (value >= amount):
                        lb[i]['inventory']['Gold Ingot'] -= amount  # Deduct the bet from user inventory if enough
                        bet_valid += 1
                        break
                
                break
        
        if bet_valid == 0:
            await ctx.send('You do not have enough gold for the bet!')
            return
        
        # Add bet to pool
        new_bet = {"id": ctx.author.id,
                    "amount": amount
                    }
        
        bet_pool.append(new_bet)
        bet_pool.sort(key=lambda x: x['amount'], reverse=True)

        # Send confirmation message
        user_ping = f'<@{ctx.author.id}>'
        bet_field = f'{gold_emoji} {amount}'

        embed_bet = discord.Embed(title='Bet made!', description='', color=0xabcdef)

        embed_bet.add_field(name='By', value=user_ping, inline=False)
        embed_bet.add_field(name='Bet', value=bet_field, inline=False)

        await ctx.send(embed=embed_bet)

        # Write changes to files
        outfile = open('data/pointless_bet_pool.json', 'w', encoding='utf-8')
        json.dump(bet_pool, outfile, indent = 4)

        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)
    
    # Display bet pool
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def pool(self, ctx):
        # Open bet pool file
        bet_pool = open('data/pointless_bet_pool.json', 'r', encoding='utf-8')
        bet_pool = json.load(bet_pool)

        # Do nothing if pool is empty
        if bet_pool == []:
            await ctx.send('Pool is empty!')
            return

        user_field = ''
        amount_field = ''
        total_bet = 0
        for b in range(len(bet_pool)):
            user_id = bet_pool[b]['id']
            user_ping = f'<@{user_id}>'

            user_field += f'{user_ping}\n'

            amount = bet_pool[b]['amount']

            amount_field += f'{amount}\n'

            total_bet += amount
        
        bet_title = f'Bet ({gold_emoji})'
        total_field = f'{gold_emoji} {total_bet}'
        
        embed_pool = discord.Embed(title='Bet pool', description='', color=0xabcdef)

        embed_pool.add_field(name='User', value=user_field, inline=True)
        embed_pool.add_field(name=bet_title, value=amount_field, inline=True)
        embed_pool.add_field(name='Total bet', value=total_field, inline=False)

        embed_pool.set_footer(text='Next person to press the pointless button gets everything in the pool.\nMay the odds be ever in your favor.')

        await ctx.send(embed=embed_pool)

# Setup function
async def setup(client):
    await client.add_cog(BetCog(client))  