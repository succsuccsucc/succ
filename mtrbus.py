# mtrbus.py
# Cog for ?mtrbus command
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

from bot import mtr_bus_stops_list, mb_routes

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class MtrbusCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def mtrbus(self, ctx, route):
        route = route.upper()
        
        for i in range(len(mb_routes)):
            if route == mb_routes[i][0] or route == '506':
                url = 'https://rt.data.gov.hk/v1/transport/mtr/bus/getSchedule'
                mb_response = requests.post(url, json={"language": "en", "routeName": route})
                mb_response = mb_response.json()

                if len(mb_response['busStop']) == 0:
                    await ctx.send('Route is not in service!')
                    return

                mb_title = mb_response['routeName']
                mb_description = mb_routes[i][1]
                embed_mtrbus = discord.Embed(title=mb_title, description=mb_description, color=0xffffff)
                
                stop_field = ''
                time_field = ''
                for a in range(len(mb_response['busStop'])):
                    bus_stop_id = mb_response['busStop'][a]['busStopId']
                    
                    time_field += mb_response['busStop'][a]['bus'][0]['departureTimeText']
                    time_field += '\n'

                    for b in range(len(mtr_bus_stops_list)):
                        if bus_stop_id == mtr_bus_stops_list[b][5]: # Stop ID on column A are untrimmed
                            if mtr_bus_stops_list[b + 1][5] == '':  # Make last stops bold
                                stop_field = stop_field + '**_' + mtr_bus_stops_list[b][4] + '_**'
                            else:
                                stop_field += mtr_bus_stops_list[b][4]
                            break
                        
                    stop_field += '\n' 
                
                stop_count = stop_field.count('\n')

                stop_field_list = stop_field.split('\n')
                time_field_list = time_field.split('\n')

                stop_field_slice = []
                time_field_slice = []

                c = 0
    
                while c < len(stop_field_list) - 1:
                    stop_field_send = ''
                    time_field_send = ''

                    stop_field_slice = stop_field_list[c : c + 11] 
                    time_field_slice = time_field_list[c : c + 11]

                    for d in range(len(stop_field_slice)):
                        stop_field_send += stop_field_slice[d]
                        stop_field_send += '\n'
                    for e in range(len(time_field_slice)):
                        time_field_send += time_field_slice[e]
                        time_field_send += '\n'

                    embed_mtrbus.add_field(name='Stop', value=stop_field_send, inline=True)
                    embed_mtrbus.add_field(name='Time', value=time_field_send, inline=True)

                    if stop_count < (c + 11):
                        split_footer = f'Stops {c + 1} to {stop_count}. Total {stop_count} stops.'
                    else:
                        split_footer = f'Stops {c + 1} to {c + 11}. Total {stop_count} stops.'

                    split_footer += '\nLast stops on the route are bolded and italicized.'

                    embed_mtrbus.set_footer(text=split_footer)

                    await ctx.send(embed=embed_mtrbus)
                    embed_mtrbus.clear_fields()

                    c += 11

                return

        await ctx.send('Route does not exist!')  

# Setup function
async def setup(client):
    await client.add_cog(MtrbusCog(client))       