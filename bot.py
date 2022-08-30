# bot.py
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

import nest_asyncio  # Fixes runtime error: asyncio.run() cannot be called from a running event loop
nest_asyncio.apply()

import config

# Change working directory to wherever bot.py is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(intents=intents, activity=discord.Game(name='Kirby and the Forgotten Land'), command_prefix='?', help_command=None)

# Load cogs (extensions)
# ?pointless and ?use are stored in the same cog due to clock item use
initial_extensions = ['succ', 'kmbtest', 'kmbeta', 'light', 'mtrfare', 'mtrbus', 'tube', 'help',  # non-pointless commands
                        'pointless_use', 'leaderboard', 'inv', 'item', 'craft', 'shop', 'buy', 'trade', 'bet_pool',  # pointless commands
                        'ballstretcher', 'morb']  # pointless item usages
                        # 'ghost']  # ghost ping handler

# Load extensions listed above
async def load_extensions():
    for extension in initial_extensions:
        await client.load_extension(extension)

# Grab list of KMB bus stops 
kmb_stops = requests.request("GET", "https://data.etabus.gov.hk/v1/transport/kmb/stop")
kmb_stops = kmb_stops.json()

# Open list of Light Rail stops
lrt = open('data/light_rail_stops.json', encoding='utf-8')
light_rail_stops = json.load(lrt)

# Open MTR fares CSV
mtr_fares = open('data/mtr_lines_fares.csv', 'r')
datareader = csv.reader(mtr_fares, delimiter=',')
fare_list = []
for row in datareader:
    fare_list.append(row)

# Open lists of MTR bus routes and stops
mtr_bus_stops = open('data/mtr_bus_stops.csv', 'r', encoding='utf-8')
datareader_mtr_bus = csv.reader(mtr_bus_stops, delimiter=',')
mtr_bus_stops_list = []
for row in datareader_mtr_bus:
    mtr_bus_stops_list.append(row)

mtr_bus_routes = open('data/mtr_bus_routes.csv', 'r', encoding='utf-8')
datareader_mb_routes = csv.reader(mtr_bus_routes, delimiter=',')
mb_routes = []
for row in datareader_mb_routes:
    mb_routes.append(row)

# Open list of ?pointless special items
item = open('data/pointless_item_list.json', 'r', encoding='utf-8')
pl_items = json.load(item)

# Open crafting recipe of special items
craft = open('data/pointless_craft_recipe.json', 'r', encoding='utf-8')
recipe = json.load(craft)

# Open special items shop catalog
shop = open('data/pointless_shop_catalog.json', 'r', encoding='utf-8')
catalog = json.load(shop)

# initialize password for protected commands
shh = None
config.shush = random.randint(1, 9999)

# initialize list of leaned people (can't press the pointless button for a round)
high_list = []

# Initialize gold and amethyst emojis for simple access
gold_emoji = "<:Gold_Ingot:1003537929525805197>"
amethyst_emoji = "<:Amethyst:1004013520796520457>"

@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild(s):\n'
            f'{guild.name}(id: {guild.id})'
        )

@client.event
async def on_message(message):

    if message.author.bot:  # Ignore message if author is bot
        return

    elif message.content == '?test':
        await message.channel.send('Yep, it\'s working.')
        return
    
    # elif 'GHOST PING' in message.content.upper():  # 'ghost ping' banning mechanism
    #     ctx = await client.get_context(message)

    #     config.shush = random.randint(1, 9999)
    #     await ctx.invoke(client.get_command('ghost'), pw=config.shush)

    await client.process_commands(message) 

# Error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown = round(error.retry_after)
        if error.retry_after > 60:
            cooldown_m = int(cooldown / 60)
            cooldown_s = int(cooldown % 60)
            await ctx.send(f'You succ\'d too fast!\nTry again after `{cooldown_m}m {cooldown_s}s`.')
        else:
            await ctx.send(f'You succ\'d too fast!\nTry again after `{cooldown}s`.')

async def main():
    async with client:
        await load_extensions()
        client.run(TOKEN)

asyncio.run(main())