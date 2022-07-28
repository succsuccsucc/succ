# bot.py
import os
import time
import requests
import datetime
import json
import csv

import discord
from dotenv import load_dotenv

from discord.ext import commands
from discord.ext.commands import CommandNotFound

# Change working directory to wherever bot.py is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, activity=discord.Game(name='Kirby and the Forgotten Land'), command_prefix='?', help_command=None)

# Grab list of KMB bus stops
kmb_stops = requests.request("GET", "https://data.etabus.gov.hk/v1/transport/kmb/stop")
kmb_stops = kmb_stops.json()

# Open list of Light Rail stops
lrt = open('data/light_rail_stops.json', encoding="utf-8",)
light_rail_stops = json.load(lrt)

# Open MTR fares CSV
mtr_fares = open('data/mtr_lines_fares.csv', 'r')
datareader = csv.reader(mtr_fares, delimiter=',')
fare_list = []
for row in datareader:
    fare_list.append(row)

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
    
    await client.process_commands(message)

@commands.cooldown(1, 10, commands.BucketType.user)
@client.command()
async def succ(ctx):
    messages = [message async for message in ctx.channel.history(limit=2)]
    cmd_msg = messages[0]
    succ_msg = messages[1]

    # Send error message if author is bot
    if succ_msg.author.bot:
        embed_author = discord.Embed(title='Message is from bot!', description='Succ can\'t consume bot messages.', color=0xff0000)
        await ctx.channel.send(embed=embed_author)
        return

    # Send error message if message has attachments
    if succ_msg.attachments:
        embed_attach = discord.Embed(title='Succ has attachment issues!', description='Message must not contain attachments.', color=0xff0000)
        await ctx.channel.send(embed=embed_attach)
        return

    # Send error message if message is longer than 1024 characters
    if (len(succ_msg.clean_content) > 1024):
        embed_too_long = discord.Embed(title='Succ can\'t handle your length!', description='Message must be no longer than 1024 characters.', color=0xff0000)
        await ctx.channel.send(embed=embed_too_long)
        return
    
    # Disable command in general channel
    if ctx.channel.id == 981207955200426037:
        return

    # Copy the 2nd last message
    content = ''
    if succ_msg.content == '':
        content = 'Message content is empty!'
    else:
        content = succ_msg.content

    embed_succ = discord.Embed(title='Slurp!', description='Your message got succ\'d', color=0xabcdef)
    embed_succ.add_field(name='Message', value=content, inline=False)  
    await ctx.channel.send(embed=embed_succ)
    await succ_msg.delete()  # Delete the 2nd last message
    return

@client.command()
async def kmbtest(ctx, stop_name):
    for i in range(len(kmb_stops['data'])):
        name_en = kmb_stops['data'][i - 1]['name_en']
        name_tc = kmb_stops['data'][i - 1]['name_tc']
        if (name_en == stop_name.upper()) or (name_tc == stop_name):
            await ctx.send(f'{name_en}\n{name_tc}')
            return
    
    await ctx.send(f'Bus stop "{stop_name}" does not exist!')

@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def kmbeta(ctx, stop_name):
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

@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def light(ctx, stop_name):
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
    
    await ctx.send(f'Light Rail stop "{stop_name}" does not exist!')
                    
@client.command()
async def mtrfare(ctx, start, end):
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

    await ctx.send('Incorrect start or destination!')

@client.command()
async def help(ctx):
    embed_help = discord.Embed(title='Help!', description='', color=0xcca6fd)

    embed_help.add_field(name='?succ', value='Consumes the last message in the channel.', inline=False)
    embed_help.add_field(name='?pointless', value='https://www.youtube.com/watch?v=EcSzq_6W1QQ', inline=False)
    embed_help.add_field(name='?test', value='Tests bot status.', inline=False)
    embed_help.add_field(name='?kmbtest <stop_name>', value='Tests if a bus stop with the given name exists.', inline=False)
    embed_help.add_field(name='?kmbeta <stop_name>', value='Gets ETA of all KMB routes at a bus stop.', inline=False)
    embed_help.add_field(name='?light <stop_name>', value='Gets train arrival times at a Light Rail stop.', inline=False)
    embed_help.add_field(name='?mtrfare <start> <end>', value='Gets the MTR fare between two stations.', inline=False)

    command_count = str(len(embed_help.fields))
    footer_string = f'Total {command_count} commands.'
    embed_help.set_footer(text=footer_string)

    await ctx.send(embed=embed_help)

# ?pointless command
class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Button",disabled=False,style=discord.ButtonStyle.gray)
    async def gray_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        button.disabled=True
        await interaction.response.edit_message(view=self, content="Hm.")

@client.command()
async def pointless(ctx):
    await ctx.send("**POINTLESS**\n**BUTTON**\nWarning: Pointless",view=Buttons())

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You succ\'d too fast!\nTry again after `{round(error.retry_after, 2)}` seconds.')

client.run(TOKEN)