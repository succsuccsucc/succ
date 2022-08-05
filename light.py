# light.py
# Cog for ?light command
import os
import requests

import discord

from discord.ext import commands

from bot import light_rail_stops

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class LightCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def light(self, ctx, stop_name):
        for i in range(len(light_rail_stops['stops'])):
            name_en = light_rail_stops['stops'][i]['name_en']
            name_ch = light_rail_stops['stops'][i]['name_ch']
            stop_id = light_rail_stops['stops'][i]['stop_id']

            if (name_en.upper() == stop_name.upper()) or (name_ch == stop_name):
                nt_request_url = "https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id="
                nt_request_url += str(stop_id)
                nt_response = requests.request("GET", nt_request_url)
                nt_response = nt_response.json()

                light_title = f'{name_en} {name_ch}'
                embed_light_title = discord.Embed(title=light_title, description='', color=0xd3a809)
                await ctx.channel.send(embed=embed_light_title)

                train_count = 0
                for a in range(len(nt_response['platform_list'])):
                    platform_id = nt_response['platform_list'][a]['platform_id']
                    platform_title = f'Platform {platform_id}'

                    embed_light = discord.Embed(title=platform_title, description='', color=0xd3a809)
                    
                    if 'end_service_status' in nt_response['platform_list'][a]:
                        embed_light.add_field(name='\u200b', value='Service ended at this platform!', inline=False)
                        await ctx.channel.send(embed=embed_light)
                        embed_light.clear_fields()
                        continue

                    for b in range(len(nt_response['platform_list'][a]['route_list'])):
                        dest_en = nt_response['platform_list'][a]['route_list'][b]['dest_en']
                        time_en = nt_response['platform_list'][a]['route_list'][b]['time_en']
                        route_no = nt_response['platform_list'][a]['route_list'][b]['route_no']
                        
                        embed_light.add_field(name='Route', value=route_no, inline=True)
                        embed_light.add_field(name='To', value=dest_en, inline=True)
                        embed_light.add_field(name='Time', value=time_en, inline=True)

                        train_count += 1
                    
                    await ctx.channel.send(embed=embed_light)
                    embed_light.clear_fields()
                
                await ctx.send(f'Total {platform_id} platform(s) and {train_count} train(s).')
                return
        
        await ctx.send(f'Light Rail stop does not exist!')

# Setup function
async def setup(client):
    await client.add_cog(LightCog(client))