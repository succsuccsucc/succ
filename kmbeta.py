# kmbeta.py
# Cog for ?kmbeta command
import os

import requests
import datetime

import discord

from discord.ext import commands

from bot import kmb_stops

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class KmbetaCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def kmbeta(self, ctx, stop_name):
        matching_stops = []
        for i in range(len(kmb_stops['data'])):
            name_en = kmb_stops['data'][i]['name_en']
            name_tc = kmb_stops['data'][i]['name_tc']
            stop_id = kmb_stops['data'][i]['stop']
            if (name_en == stop_name.upper()) or (name_tc == stop_name):
                matching_stops.append(stop_id)

        if matching_stops == []:
            await ctx.send(f'Bus stop "{stop_name}" does not exist!')
            return
        
        display_value = 0
        cut_count = 0

        etitle = 'ETA at ' + stop_name.upper()
        embed_etitle = discord.Embed(title=etitle, description='', color=0x00ff00)
        await ctx.channel.send(embed=embed_etitle)

        for item in matching_stops:
            eta_request_url = "https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/"
            eta_request_url += item
            stop_eta = requests.request("GET", eta_request_url)
            stop_eta = stop_eta.json()
            
            embed_kmbeta = discord.Embed(title='\u200b', description='', color=0x00ff00)
            
            for a in range(len(stop_eta['data'])):
                if (stop_eta['data'][a]['route'] == stop_eta['data'][a - 1]['route']) and (stop_eta['data'][a]['dest_en'] == stop_eta['data'][a - 1]['dest_en']):
                    continue

                route = stop_eta['data'][a]['route']
                dest_en = stop_eta['data'][a]['dest_en']
                eta_iso = stop_eta['data'][a]['eta']

                if eta_iso != None:
                    eta_dt = datetime.datetime.fromisoformat(str(eta_iso))
                else:
                    continue
                
                display_value += 1
                cut_count += 1
                
                now = datetime.datetime.now(datetime.timezone.utc)
                time_diff = eta_dt - now
                tmins = time_diff.total_seconds() / 60
                tmins = str(round(tmins))
                if int(tmins) < 0:
                    tmins = 'Arrived'
                elif int(tmins) == 0:
                    tmins = 'Arriving'

                embed_kmbeta.add_field(name='Route', value=route, inline=True)
                embed_kmbeta.add_field(name='Destination', value=dest_en, inline=True)
                embed_kmbeta.add_field(name='ETA', value=tmins, inline=True)

                if cut_count == 6 and a != 0:
                    if len(embed_kmbeta) != 1:
                        await ctx.channel.send(embed=embed_kmbeta)
                    embed_kmbeta.clear_fields()
                    cut_count = 0
                    continue

            if len(embed_kmbeta) != 1:
                await ctx.channel.send(embed=embed_kmbeta)
            cut_count = 0
                
        await ctx.send('Total ' + str(len(matching_stops)) + ' stop(s) and ' + str(display_value) + ' route(s).')

# Setup function
async def setup(client):
    await client.add_cog(KmbetaCog(client))