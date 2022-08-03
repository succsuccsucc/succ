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

from collections import OrderedDict

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

# initialize password for resetting ?pointless cooldown using clock item
shh = None

# initialize list of leaned people (can't press the pointless button for a round)
high_list = []

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

    # Disable command in general channel
    if ctx.channel.id == 981207955200426037:
        return
    
    # Send error message if author is bot
    if succ_msg.author.bot:
        embed_author = discord.Embed(title='Message is from bot!', description='Succ can\'t consume bot messages.', color=0xff0000)
        await ctx.channel.send(embed=embed_author)
        return

    # If message has attachments
    if succ_msg.attachments:
        embed_attach = discord.Embed(title='Slurp!', description='Your message got succ\'d', color=0xabcdef)
        await ctx.channel.send(embed=embed_attach)

        await ctx.send(succ_msg.content, files=[await f.to_file() for f in succ_msg.attachments])

        await succ_msg.delete()  # Delete the 2nd last message

        return

    # Send error message if message is longer than 1024 characters
    if (len(succ_msg.clean_content) > 1024):
        embed_too_long = discord.Embed(title='Succ can\'t handle your length!', description='Message must be no longer than 1024 characters.', color=0xff0000)
        await ctx.channel.send(embed=embed_too_long)
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

    await ctx.send('Start or destination does not exist!')

@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def mtrbus(ctx, route):
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
                
@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def help(ctx, page=None):
    if not page:
        embed_help = discord.Embed(title='Help!', description='', color=0xcca6fd)

        embed_help.add_field(name='?succ', value='Consumes the last message in the channel.', inline=False)
        embed_help.add_field(name='?pointless', value='https://www.youtube.com/watch?v=EcSzq_6W1QQ', inline=False)
        embed_help.add_field(name='?test', value='Tests bot status.', inline=False)
        embed_help.add_field(name='?kmbtest <stop_name>', value='Tests if a bus stop with the given name exists.', inline=False)
        embed_help.add_field(name='?kmbeta <stop_name>', value='Gets ETA of all KMB routes at a bus stop.', inline=False)
        embed_help.add_field(name='?light <stop_name>', value='Gets train arrival times at a Light Rail stop.', inline=False)
        embed_help.add_field(name='?mtrfare <start> <end>', value='Gets the MTR fare between two stations.', inline=False)
        embed_help.add_field(name='?mtrbus <route>', value='Gets ETA at all bus stops of an MTR Bus route.', inline=False)

        command_count = str(len(embed_help.fields))
        footer_string = f'Total {command_count} commands in this page.\nUse ?help pointless for commands about the pointless button.'
        embed_help.set_footer(text=footer_string)

        await ctx.send(embed=embed_help)

    if page == 'pointless':
        embed_help = discord.Embed(title='Help!', description='Commands about the pointless button', color=0xcca6fd)
        
        embed_help.add_field(name='?pointless', value='https://www.youtube.com/watch?v=EcSzq_6W1QQ', inline=False)
        embed_help.add_field(name='?leaderboard', value='Dick measuring contest.', inline=False)
        embed_help.add_field(name='?inv [username]', value='Check a user\'s inventory.', inline=False)
        embed_help.add_field(name='?use <item> [target]', value='Use an item in your inventory.', inline=False)
        embed_help.add_field(name='?craft <item>', value='Craft items into another item.', inline=False)

        command_count=str(len(embed_help.fields))
        footer_string = f'Total {command_count} commands in this page.'
        embed_help.set_footer(text=footer_string)

        await ctx.send(embed=embed_help)

# ?pointless command
class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Button",disabled=False,style=discord.ButtonStyle.gray)
    async def gray_button(self,interaction:discord.Interaction,button:discord.ui.Button): 
        # Disable command if button is already disabled (someone pressed already)
        if button.disabled == True:
            await interaction.response.send_message(content='Too slow!', ephemeral=True)
            return
        
        button.disabled=True

        await interaction.response.edit_message(view=self, content="Hm.")

        # Disable, notify, and resend command if user is high (leaned)
        if interaction.user.id in high_list:
            messages = [message async for message in interaction.channel.history(limit=1)]
            await messages[0].delete()
            
            high_response = f'{interaction.user.mention} is high and cannot press the button!'
            await interaction.channel.send(high_response)

            await interaction.channel.send("**POINTLESS**\n**BUTTON**\nWarning: Pointless",view=Buttons())

            return
        
        # Reset the high list after a pointless button is summoned
        high_list.clear()

        leaderboard_file = open('data/pointless_leaderboard.json', encoding='utf-8')
        leaderboard = json.load(leaderboard_file)

        new = 0  # Check if user is on leaderboard already
        for i in range(len(leaderboard)):
            if interaction.user.id == leaderboard[i]['id']:
                leaderboard[i]['score'] += 1

                leaderboard.sort(key=lambda x: x['score'], reverse=True)

                outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
                json.dump(leaderboard, outfile, indent = 4)
                new = 1
                break
        
        if new == 0:
            new_user = {"id": interaction.user.id,
                        "score": 1
                        }
            
            # Use fetch_user instead of get_user!
            # userinfo = await client.fetch_user(740098404688068641)
            # print(userinfo.name)

            leaderboard.append(new_user)
            leaderboard_file.seek(0)

            leaderboard.sort(key=lambda x: x['score'], reverse=True)

            outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
            json.dump(leaderboard, outfile, indent = 4)

        # Draw special item
        item_yn = random.randint(1, 10)
        if item_yn <= 5:
            rarity_total = pl_items[len(pl_items) - 1]['rarity']
            
            draw_variable = random.randint(1, rarity_total)

            for a in range(len(pl_items)):
                if ((draw_variable <= pl_items[a]['rarity']) and (draw_variable > pl_items[a - 1]['rarity']))\
                    or (a == 0 and draw_variable <= pl_items[a]['rarity']):
                    give_index = a
                    break
            
            for b in range(len(leaderboard)):
                if interaction.user.id == leaderboard[b]['id']:
                    if 'inventory' not in leaderboard[b]:  # Add inventory key to user if it doesn't exist
                        leaderboard[b]['inventory'] = {}
                    
                    give_name = pl_items[give_index]['name']
                    give_emoji = pl_items[give_index]['emoji']

                    if pl_items[give_index]['name'] not in leaderboard[b]['inventory']:
                        leaderboard[b]['inventory'][give_name] = 1
                    else:
                        leaderboard[b]['inventory'][give_name] += 1
                    
                    user_id = leaderboard[b]['id']
                    user_ping = f'<@{user_id}>'

                    outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
                    json.dump(leaderboard, outfile, indent = 4)

                    await interaction.channel.send(f'{user_ping} got 1 {give_emoji} `{give_name}`!')

                    return

@commands.cooldown(1, 900, commands.BucketType.guild)
@client.command()
async def pointless(ctx, pw=None):
    if not pw:
        await ctx.send("**POINTLESS**\n**BUTTON**\nWarning: Pointless",view=Buttons())
    elif pw == shh:
        pointless.reset_cooldown(ctx)

@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def leaderboard(ctx):
    lb_file = open('data/pointless_leaderboard.json', 'r')
    lb = json.load(lb_file)

    name_list = []
    score_list = []
    rank_list = []
    
    for i in range(len(lb)):
        user_id = lb[i]['id']

        user_name = f'<@{user_id}>'
        name_list.append(user_name)

        score = lb[i]['score']
        score_list.append(str(score))

        rank_list.append(str(i + 1))

    if len(rank_list) >= 1:
        rank_list[0] = ':trophy: ' + rank_list[0]
    if len(rank_list) >= 2:
        rank_list[1] = ':second_place: ' + rank_list[1]
    if len(rank_list) >= 3:
        rank_list[2] = ':third_place: ' + rank_list[2]
    
    name_field = ''
    score_field = ''
    rank_field = ''
    
    name_field = '\n'.join(name_list)
    score_field = '\n'.join(score_list)
    rank_field = '\n'.join(rank_list)
    
    embed_leaderboard = discord.Embed(title='?pointless leaderboard', description='Get points by pressing the pointless button!', color=0xabcdef)

    embed_leaderboard.add_field(name='Rank', value=rank_field, inline=True)
    embed_leaderboard.add_field(name='Name', value=name_field, inline=True)
    embed_leaderboard.add_field(name='Score', value=score_field, inline=True)

    people_count = len(name_list)
    footer_leaderboard = f'Total {people_count} people.'
    embed_leaderboard.set_footer(text=footer_leaderboard)

    await ctx.send(embed=embed_leaderboard)

@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def inv(ctx, user=None):
    if not user:
        user_id = ctx.author.id
    else:
        user_id = user[2 : -1]

    user_name = await client.fetch_user(user_id)
    user_name = user_name.name
    
    inv_title = f'Inventory of {user_name}'
    
    embed_inv = discord.Embed(title=inv_title, description='', color=0xabcdef)

    lb_file = open('data/pointless_leaderboard.json', 'r')
    lb = json.load(lb_file)

    # Display gold and amethyst count in description
    inv_description = ''
    
    for i in range(len(lb)):
        if int(user_id) == lb[i]['id']:

            if 'inventory' not in lb[i]:
                break

            for c in range(len(pl_items)):
                for key, value in lb[i]['inventory'].items():
                    item_name = key

                    if item_name == pl_items[c]['name']:
                        item_desc = pl_items[c]['description']
                        item_emoji = pl_items[c]['emoji']

                        # Add gold count to description string for display
                        if item_name == "Gold Ingot":
                            inv_description += item_emoji + ' ' + str(value)

                        item_field_title = item_emoji +' '+  item_name + ': ' + str(value)

                        embed_inv.add_field(name=item_field_title, value=item_desc, inline=False)
                        
                        break

            # Compose inventory of crafted items
            crafted_inv_title = f'Crafted items of {user_name}'

            embed_crafted_inv = discord.Embed(title=crafted_inv_title, description='', color=0xabcdef)

            for d in range(len(recipe)):
                for key, value in lb[i]['inventory'].items():
                    thing_name = key

                    if thing_name == recipe[d]['name']:
                        thing_desc = recipe[d]['description']
                        thing_emoji = recipe[d]['emoji']

                        if thing_name == "Amethyst":
                            inv_description += ' | ' + thing_emoji + ' ' + str(value)

                        thing_field_title = thing_emoji + ' ' + thing_name + ': ' + str(value)

                        embed_crafted_inv.add_field(name=thing_field_title, value=thing_desc, inline=False)

                        break
                
            # Send inventory
            embed_inv.description = inv_description
            await ctx.send(embed=embed_inv)
            
            if len(embed_crafted_inv) != (len(embed_crafted_inv.title) + len(embed_crafted_inv.description)):  # Only send if there are crafted items in inventory
                await ctx.send(embed=embed_crafted_inv)

            return
        
    await ctx.send('User does not have any items!')

# Use an item
@client.command()
async def use(ctx, item, target=None):
    # Check if item exists
    # Check in normal items list
    exist = 0
    for a in range(len(pl_items)):
        if item.upper() == pl_items[a]['name'].upper():
            exist += 1
            break
    
    # Check in crafted items recipe
    for c in range(len(recipe)):
        if item.upper() == recipe[c]['name'].upper():
            exist += 1
            break

    if exist == 0:
        nonexist_item_string = f'Item `{item}` does not exist!'
        await ctx.send(nonexist_item_string)
        return

    # Look for user inventory
    lb_file = open('data/pointless_leaderboard.json', 'r')
    lb = json.load(lb_file)

    op_id = ctx.author.id
    
    valid_use = 0

    # Check if user has the item and spend it
    for i in range(len(lb)):
        if op_id == lb[i]['id']:
            for key, value in lb[i]['inventory'].items():
                if item.upper() == key.upper():
                    lb[i]['inventory'][key] -= 1
                    valid_use += 1
                    break   
            if valid_use == 0:
                await ctx.send('You do not have this item!')
                return
    
            # Remove item from user's inventory if count is 0
            for key, value in list(lb[i]['inventory'].items()):
                if value == 0:
                    del lb[i]['inventory'][key]

            break
    
    # Apply corresponding effect of item used
    used = 0  # Do not spend item if item is unusable
    
    # Normal items
    if item.upper() == 'CLOCK':
        global shh
        shh = random.randint(1, 9999)  # To prevent cooldown reset from being triggered without using a clock

        await ctx.invoke(client.get_command('pointless'), pw=shh)

        user_name = await client.fetch_user(ctx.author.id)
        user_name = user_name.name
        
        clock_used_title = f'{user_name} used Clock!'

        embed_clock_used = discord.Embed(title=clock_used_title, description='?pointless cooldown is now reset!', color=0xabcdef)
        await ctx.send(embed=embed_clock_used)

        used += 1

    elif item.upper() == 'LEAN':
        if not target:
            await ctx.send('You must specify someone you want to give Lean to!')
            return
        else:
            target_id = int(target[2 : -1])  # Slice target user ID from ping

            # Check if target exists
            target_exist = 0  
            for b in range(len(lb)):  
                if lb[b]['id'] == target_id:
                    target_exist += 1
                    break
            
            if target_exist == 0:
                await ctx.send('Invalid user!')
                return

            # Add target user to the high list
            high_list.append(target_id)

            # Send confirmation message
            user_name = await client.fetch_user(ctx.author.id)
            user_name = user_name.name
            
            lean_used_title = f'{user_name} used Lean!'
            lean_used_description = f'{target} is now high! They cannot press the pointless button when it is next summoned.'
           
            embed_lean_used = discord.Embed(title=lean_used_title, description=lean_used_description, color=0xabcdef)
            await ctx.send(embed=embed_lean_used)

            used += 1

    # Crafted items
    elif item.upper() == 'GUSHING GRANNY':
        if not target:
            target_id = ctx.author.id
        else:
            target_id = int(target[2 : -1])  # Slice target user ID from ping

        # Check if target exists
        target_exist = 0  
        for b in range(len(lb)):  
            if lb[b]['id'] == target_id:
                target_exist += 1
                break

        if target_exist == 0:
            await ctx.send('Invalid user!')
            return
            
        # Check if target is high, remove target from high list if yes
        target_high = 0
        for value in high_list:
            if target_id == value:
                high_list.remove(value)
                target_high += 1
                break
        
        if target_high == 0:
            await ctx.send('Target is not high!')
            return

        # Send confirmation message
        user_name = await client.fetch_user(ctx.author.id)
        user_name = user_name.name

        gushing_used_title = f'{user_name} used Gushing Granny!'
        gushing_used_description = f'{target} is no longer high!'
        
        embed_gushing_used = discord.Embed(title=gushing_used_title, description=gushing_used_description, color=0xabcdef)
        await ctx.send(embed=embed_gushing_used)

        used += 1

    else:
        await ctx.send('Item is unusable!')

    # Confirm spend item after using
    # Write changes to leaderboard
    if used == 1:
        outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
        json.dump(lb, outfile, indent = 4)

@commands.cooldown(1, 5, commands.BucketType.guild)
@client.command()
async def craft(ctx, item, amount=1):
    # Check if amount is 0
    if amount == 0:
        await ctx.invoke(client.get_command('succ'))
        return

    # Check if item exists
    # Check in crafted items recipe
    exist = 0
    for i in range(len(recipe)):
        if item.upper() == recipe[i]['name'].upper():
            product_index = i
            product_name = recipe[i]['name']
            exist += 1
            break

    if exist == 0:
        nonexist_item_string = f'Item `{item}` does not exist or is not craftable!'
        await ctx.send(nonexist_item_string)
        return

    # Open user inventory
    lb_file = open('data/pointless_leaderboard.json', 'r')
    lb = json.load(lb_file)
    
    user_id = ctx.author.id

    # Find user's entry in leaderboard
    for a in range(len(lb)):
        if lb[a]['id'] == user_id:
            user_index = a
            break

    # Check if user has enough ingredients
    enough_check = 0
    for p_key, p_value in recipe[product_index]['ingredients'].items():
        for i_key, i_value in lb[user_index]['inventory'].items():
            if i_key == p_key:
                if i_value >= (p_value * amount):
                    lb[user_index]['inventory'][i_key] -= (p_value * amount)
                    enough_check += 1
                    break
                else:
                    break

    # Give crafted item if have enough ingredients
    if enough_check == len(recipe[product_index]['ingredients']):
        if recipe[product_index]['name'] not in lb[user_index]['inventory']:
            lb[user_index]['inventory'][product_name] = amount
        else:
            lb[user_index]['inventory'][product_name] += amount  
    else:  # Send error message if not enough ingredients
        await ctx.send('You do not have the required ingredients!')
        return

    # Remove item(s) from user's inventory if count is 0
    for key, value in list(lb[user_index]['inventory'].items()):
        if value == 0:
            del lb[user_index]['inventory'][key]
        
    # Send confirmation message
    craft_confirm_title = f'Successfully crafted {product_name}!'
    embed_craft_confirm = discord.Embed(title=craft_confirm_title, description='', color=0xabcdef)

    ingredient_field = ''
    for key_2, value_2 in recipe[product_index]['ingredients'].items():
        for b in range(len(pl_items)):
            if key_2 == pl_items[b]['name']:
                ingredient_field += pl_items[b]['emoji'] + ' '
                break

        ingredient_field += key_2 + ' x' + str(value_2 * amount) + '\n'
    
    embed_craft_confirm.add_field(name='Used', value=ingredient_field, inline=False)

    product_field = recipe[product_index]['emoji'] + ' ' + product_name + ' x' + str(amount)

    embed_craft_confirm.add_field(name='Crafted', value=product_field, inline=False)

    await ctx.send(embed=embed_craft_confirm)
    
    # Write changes to leaderboard
    outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
    json.dump(lb, outfile, indent = 4)

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

client.run(TOKEN)