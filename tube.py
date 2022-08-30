# tube.py
# Cog for ?tube command
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

from operator import itemgetter

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class TubeCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def tube(self, ctx, station='', line=''):
        # Check if line is valid
        if line.upper() == 'HAMMERSMITH & CITY':
            line_id = 'hammersmith-city'
        elif line.upper() == 'WATERLOO & CITY':
            line_id = 'waterloo-city'
        else:
            line_id = line.lower()
        
        lines = ['bakerloo', 'central', 'circle', 'district', 'hammersmith-city', 'jubilee', 'metropolitan', 'northern', 'piccadilly', 'victoria', 'waterloo-city']

        if line_id not in lines:
            await ctx.send('Invalid line!')
            return
        else:
            eta_link = f'https://api.tfl.gov.uk/Line/{line_id}/Arrivals'

        eta = requests.request("GET", eta_link)  # Get ETA data for line
        eta = eta.json()

        # Filter data by station
        trains = []
        for i in range(len(eta)):
            if station.upper().split() == eta[i]['stationName'][0: -20].upper().split()[ : (len(station.upper().split()) + 1)]:
                trains.append(eta[i])
        
        if trains == []:  # Return if no trains found in the station
            await ctx.send('No trains found!\nIs your station nonexistent, or not served by the line?')
            return
        
        trains = sorted(trains, key=lambda k: (k['platformName'].lower(), k['timeToStation']))  # Sort trains by destination, then by time

        # Display results
        line_name_display = trains[0]['lineName'] + ' line'

        embed_tube = discord.Embed(title=trains[0]['stationName'][0: -20], description=line_name_display, color=0xde2110)

        dest_field = ''
        plat_field = ''
        time_field = ''
        for a in range(len(trains)):
            dest_field += trains[a]['towards'] + '\n'
            plat_field += trains[a]['platformName'][-1] + '\n'
            
            # Convert ETA from s to m:s
            if trains[a]['timeToStation'] > 60:
                time_min = int(trains[a]['timeToStation'] / 60)
                time_sec = int(trains[a]['timeToStation'] % 60)
                time_field += f'{time_min}m {time_sec}s' + '\n'
            else:
                time_sec = trains[a]['timeToStation']
                time_field += f'{time_sec}s' + '\n'
        
        embed_tube.add_field(name='Platform', value=plat_field, inline=True)
        embed_tube.add_field(name='To', value=dest_field, inline=True)
        embed_tube.add_field(name='Time', value=time_field, inline=True)

        train_count = len(trains)
        tube_footer = f'Total {train_count} trains.\nMind the gap.'
        embed_tube.set_footer(text=tube_footer)

        await ctx.send(embed=embed_tube)

# Setup function
async def setup(client):
    await client.add_cog(TubeCog(client))
