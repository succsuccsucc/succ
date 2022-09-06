# train.py
# Cog for ?train command
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

from typing import List

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

mtr_stations = open('data/mtr_stations.json', encoding="utf-8")
mtr_stations = json.load(mtr_stations)

# Reserved for migration to slash commands
# autocomplete = []
# for i in range(len(mtr_stations)):
#     autocomplete.append(mtr_stations['stations'][i]['name_en'])

line_dict = {
    "AEL": "Airport Express",
    "TCL": "Tung Chung Line",
    "TML": "Tuen Ma Line",
    "TKL": "Tseung Kwan O Line",
    "EAL": "East Rail Line"
}

line_colors = {
    "AEL": 0x00888a,
    "TCL": 0xf7943e,
    "TML": 0x923011,
    "TKL": 0x7d499d,
    "EAL": 0x53b7e8
}

class TrainCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def train(self, ctx, station=''):
        # Check if station exist
        for a in range(len(mtr_stations['stations'])):
            if station.upper() == mtr_stations['stations'][a]['name_en'].upper():
                sta_id = mtr_stations['stations'][a]['sta_id']
                lines = mtr_stations['stations'][a]['lines']

                for line in lines:
                    url = f'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={line}&sta={sta_id}'

                    train_eta = requests.request("GET", url)
                    train_eta = train_eta.json()

                    # Success
                    if train_eta['status'] == 1 and train_eta['sys_time'] != '-':
                        train_title = mtr_stations['stations'][a]['name_en']
                        train_desc = line_dict[line]  # Get full name of line from line ID
                        train_color = line_colors[line]  # Get color of line from line ID

                        # Prepare ETA message embed
                        embed_traineta = discord.Embed(title=train_title, description=train_desc, color=train_color)

                        data_id = f'{line}-{sta_id}'

                        plat_field = ''
                        dest_field = ''
                        time_field = ''

                        if 'UP' in train_eta['data'][data_id]:
                            for b in range(len(train_eta['data'][data_id]['UP'])):
                                # Add platform number to message
                                plat_field += train_eta['data'][data_id]['UP'][b]['plat'] + '\n'

                                # Add destination to message
                                for c in range(len(mtr_stations['stations'])):
                                    if train_eta['data'][data_id]['UP'][b]['dest'] == mtr_stations['stations'][c]['sta_id']:
                                        dest_field += mtr_stations['stations'][c]['name_en'] + '\n'
                                        break
                                
                                # Calculate ETA in minutes
                                time_string = train_eta['data'][data_id]['UP'][b]['time'][11:]
                                time_coming = datetime.datetime.strptime(time_string, "%H:%M:%S")

                                time_now_string = train_eta['curr_time'][11:]
                                time_now = datetime.datetime.strptime(time_now_string, "%H:%M:%S")

                                eta_minutes = str(time_coming - time_now)[-5:-3]
                                if int(eta_minutes) < 0:
                                    eta_minutes = 'Arrived'
                                
                                # Add ETA to message
                                time_field += eta_minutes + '\n'
                            
                        if 'DOWN' in train_eta['data'][data_id]:
                            for d in range(len(train_eta['data'][data_id]['DOWN'])):
                                # Add platform number to message
                                plat_field += train_eta['data'][data_id]['DOWN'][d]['plat'] + '\n'

                                # Add destination to message
                                for e in range(len(mtr_stations['stations'])):
                                    if train_eta['data'][data_id]['DOWN'][d]['dest'] == mtr_stations['stations'][e]['sta_id']:
                                        dest_field += mtr_stations['stations'][e]['name_en'] + '\n'
                                        break
                                
                                # Calculate ETA in minutes
                                time_string = train_eta['data'][data_id]['DOWN'][d]['time'][11:]
                                time_coming = datetime.datetime.strptime(time_string, "%H:%M:%S")

                                time_now_string = train_eta['curr_time'][11:]
                                time_now = datetime.datetime.strptime(time_now_string, "%H:%M:%S")

                                eta_minutes = str(time_coming - time_now)[-5:-3]
                                if int(eta_minutes) < 0:
                                    eta_minutes = 'Arrived'
                                
                                # Add ETA to message
                                time_field += eta_minutes + '\n'
                        
                        embed_traineta.add_field(name='Platform', value=plat_field, inline=True)
                        embed_traineta.add_field(name='To', value=dest_field, inline=True)
                        embed_traineta.add_field(name='Time (min)', value=time_field, inline=True)

                        # Send it
                        await ctx.send(embed=embed_traineta)
                
                    # Data absence
                    elif train_eta['status'] == 1 and train_eta['sys_time'] == '-':
                        await ctx.send('Error: No Data for this line at this station!')
                    
                    # Special train arrangements/suspension
                    elif train_eta['status'] == 0:
                        special_message = f'Special arrangement in place! Message from MTR:\n> '
                        special_message += train_eta['message']

                        await ctx.send(special_message)
                        return

                return

    # Reserved for migration to slash commands
    # @train.autocomplete('train')
    # async def train_autocomplete(
    #     interaction: discord.Interaction,
    #     current: str,
    # ) -> List[app_commands.Choice[str]]:
    #     stations = autocomplete
    #     return [
    #         app_commands.Choice(name=station, value=station)
    #         for station in stations if current.lower() in station.lower()
    #     ]

# Setup function
async def setup(client):
    await client.add_cog(TrainCog(client))