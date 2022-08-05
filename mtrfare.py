# mtrfare.py
# Cog for ?mtrfare command
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

from bot import fare_list

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class MtrfareCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def mtrfare(self, ctx, start, end):
        for i in range(len(fare_list)):
            if (start.upper() == fare_list[i][0].upper()) and (end.upper() == fare_list[i][2].upper()):
                oct_adt_fare = '$' + fare_list[i][4]  # Octopus (Adult)
                oct_std_fare = '$' + fare_list[i][5]  # Octopus (Student) (half price)
                single_adt_fare = '$' + fare_list[i][6]  # Ticket (Adult)
                oct_con_child_fare = '$' + fare_list[i][7]  # Octopus (Child) (half price)
                oct_con_elderly_fare = '$' + fare_list[i][8]  # Octopus (Elderly) ($2)
                oct_con_pwd_fare = '$' + fare_list[i][9]  # Octopus (Disability) ($2)
                single_con_child_fare = '$' + fare_list[i][10] # Ticket (Child) (half price)
                single_con_elderly_fare = '$' + fare_list[i][11]  # Ticket (Elderly) (half price)
            
                mtrfare_title = fare_list[i][0] + ' to ' + fare_list[i][2]
                embed_mtrfare = discord.Embed(title=mtrfare_title, description='', color=0x00ff00)
                embed_mtrfare.add_field(name='Adult (Octopus)', value=oct_adt_fare, inline=True)
                embed_mtrfare.add_field(name='Adult (Ticket)', value=single_adt_fare, inline=True)
                embed_mtrfare.add_field(name='Student (Octopus)', value=oct_std_fare, inline=False)
                embed_mtrfare.add_field(name='Child (Octopus)', value=oct_con_child_fare, inline=True)
                embed_mtrfare.add_field(name='Child (Ticket)', value=single_con_child_fare, inline=True)
                
                embed_mtrfare.add_field(name='\u200b', value='\u200b', inline=False)

                embed_mtrfare.add_field(name='Elderly (Octopus)', value=oct_con_elderly_fare, inline=True)
                embed_mtrfare.add_field(name='Elderly (Ticket)', value=single_con_elderly_fare, inline=True)
                embed_mtrfare.add_field(name='Disability (Octopus)', value=oct_con_pwd_fare, inline=False)

                mtrfare_footer = 'Students aged 12 and above and eligible persons with disabilities aged 12 to 64 travelling with Single Journey Tickets are required to pay full adult fare.\nFrom now until 1 January 2023, passengers can enjoy 3.8% Fare Rebate for every fare-paying trip using Octopus.'
                
                if fare_list[i][0].upper() == fare_list[i][2].upper():
                    embed_mtrfare.clear_fields()
                    same_station = 'Entrance within 20 minute: Paying minimum fare of single ride ticket\n\
                                    Within 150 minute: $10 for adult, $5 for Child, Minimum fare of single ride ticket for elderly and PwD\n\
                                    After 150 minutes: Paying maximum fare of single ride ticket\n\n\
                                    https://cdn.discordapp.com/attachments/805744932975280158/1001367948604223508/unknown.png'               
                    
                    if (fare_list[i][0] == 'Lo Wu') or (fare_list[i][0] == 'Lok Ma Chau'):
                        same_station = 'Lo Wu/Lok Ma Chau Regulation\n\
                                        Within 20 minutes: Minimum single ride ticket fare of that station\n\
                                        Within 150 minutes: Except elderlies, PwD and Concessionary Travel Scheme user,\n\
                                        - First class user (Using first class single ride ticket/Tapped the first class processor/Using QR code, selected first class): Minimum fee of the first class, i.e. Minimum of adult/concessionary fare and first class premium of that station.\n\
                                        - Others: Current minimum fare for a single journey of that station. However, concessionary Travel Scheme user not applicable.\n\n\
                                        https://cdn.discordapp.com/attachments/805744932975280158/1001367948604223508/unknown.png'
                    
                    embed_mtrfare.add_field(name='Same station entry and exit', value=same_station, inline=False)

                embed_mtrfare.set_footer(text=mtrfare_footer)

                await ctx.send(embed=embed_mtrfare)
                return

        await ctx.send('Start or destination does not exist!')

# Setup function
async def setup(client):
    await client.add_cog(MtrfareCog(client))