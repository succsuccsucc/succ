# kmbtest.py
# cog for ?kmbtest command
import os
import discord

from discord.ext import commands

from bot import kmb_stops  # Get global variables from bot.py

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class KmbtestCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.guild_only()
    @commands.command()
    async def kmbtest(self, ctx, stop_name):
        for i in range(len(kmb_stops['data'])):
            name_en = kmb_stops['data'][i - 1]['name_en']
            name_tc = kmb_stops['data'][i - 1]['name_tc']
            if (name_en == stop_name.upper()) or (name_tc == stop_name):
                await ctx.send(f'{name_en}\n{name_tc}')
                return
        
        stop_nonexist = f'Bus stop "{stop_name}" does not exist!'
        if len(stop_nonexist) > 1024:
            await ctx.send('Bot response too long! Check your command.')
            return
        await ctx.send(stop_nonexist)

# Setup function
async def setup(client):
    await client.add_cog(KmbtestCog(client))