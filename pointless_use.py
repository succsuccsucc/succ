# pointless_use.py
# Cog for ?pointless and ?use commands
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

from bot import high_list, pl_items, recipe, catalog, shh

# List of users protected by Conduit
conduit_list = []

# Load json containing Train Ticket usage scenarios
scenarios_file = open('data/pointless_train_ticket_scenarios.json', encoding='utf-8')
scenarios = json.load(scenarios_file)

# Change working directory to wherever this is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Button function
class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Button",disabled=False,style=discord.ButtonStyle.gray)
    async def gray_button(self,interaction:discord.Interaction,button:discord.ui.Button): 
        # Disable command if button is already disabled (someone pressed already)
        if button.disabled == True:
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
                        "score": 1,
                        "inventory": {
                            "Gold Ingot": 0,
                            "Amethyst": 0
                        }
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
                        leaderboard[b]['inventory'] = {"Gold Ingot": 0,
                                                        "Amethyst": 0
                                                        }
                    
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

class PointlessCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 899, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def pointless(self, ctx, pw=None):
        if not pw:
            await ctx.send("**POINTLESS**\n**BUTTON**\nWarning: Pointless",view=Buttons())
        elif pw == shh:
            self.pointless.reset_cooldown(ctx)

    # Use an item
    @commands.command()
    @commands.guild_only()
    async def use(self, ctx, item, target=None):
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
        
        # Check in shop items recipe
        for d in range(len(catalog)):
            if item.upper() == catalog[d]['name'].upper():
                exist += 1
                break

        if exist == 0:
            nonexist_item_string = f'Item `{item}` does not exist!'
            
            if len(nonexist_item_string) > 1024:
                await ctx.send('Bot response too long! Check your command.')
                return
                
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
                    if (key != 'Gold Ingot') and (key != 'Amethyst') and (value == 0):
                        del lb[i]['inventory'][key]

                break
        
        # Check if target id is integer
        target_is_int = 0
        if (target != None) and (len(target) >= 3):
            target_num = target[2 : -1]
            if target_num.isdigit():
                target_is_int += 1
        
        if not target:
            target_is_int += 1

        if target_is_int == 0:
            await ctx.send('Invalid target!')
            return
        
        # Apply corresponding effect of item used
        used = 0  # Do not spend item if item is unusable
        
        if item.upper() == 'CLOCK':
            global shh
            shh = random.randint(1, 9999)  # To prevent cooldown reset from being triggered without using a clock

            await ctx.invoke(self.client.get_command('pointless'), pw=shh)

            user_name = await self.client.fetch_user(ctx.author.id)
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
                
                # Make a check if user is protected by Conduit
                lean_blocked = 0
                if target_id in conduit_list:
                    conduit_check = random.randint(1, 10)
                    if conduit_check <= 3:  # Check failed
                        conduit_list.remove(target_id)

                        target_name = await self.client.fetch_user(target_id)
                        target_name = target_name.name

                        conduit_failed_title = f'{target_name}\'s Conduit failed!'
                        conduit_failed_desc = f'{target} no longer has Conduit Power.'

                        embed_conduit_failed = discord.Embed(title=conduit_failed_title, description=conduit_failed_desc, color=0xff0000)
                        await ctx.send(embed=embed_conduit_failed)

                    else:
                        target_name = await self.client.fetch_user(target_id)
                        target_name = target_name.name

                        conduit_success_title = f'{target_name} is protected by Conduit!'
                        conduit_success_desc = f'{target} is not affected by the Lean.'

                        embed_conduit_success = discord.Embed(title=conduit_success_title, description=conduit_success_desc, color=0xabcdef)
                        await ctx.send(embed=embed_conduit_success)

                        lean_blocked += 1

                if lean_blocked == 0:
                    # Add target user to the high list
                    high_list.append(target_id)

                    # Send confirmation message
                    user_name = await self.client.fetch_user(ctx.author.id)
                    user_name = user_name.name

                    lean_used_title = f'{user_name} used Lean!'
                    lean_used_description = f'{target} is now high! They cannot press the pointless button when it is next summoned.'
                
                    embed_lean_used = discord.Embed(title=lean_used_title, description=lean_used_description, color=0xabcdef)
                    await ctx.send(embed=embed_lean_used)

                used += 1

        # Cum Chalice has the same effect as Gushing Granny if check success
        elif (item.upper() == 'GUSHING GRANNY') or (item.upper() == 'CUM CHALICE'):
            if not target:
                target_id = ctx.author.id
                target = f'<@{ctx.author.id}>'
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
                    target_high += 1
                    break
            
            if target_high == 0:
                await ctx.send('Target is not high!')
                return
            
            # Make a check if user used Cum Chalice
            cum_check = 0
            if item.upper() == 'CUM CHALICE':
                cum_check = random.randint(1, 2)
            if (cum_check == 2) or item.upper() == 'GUSHING GRANNY':  # Remove target as usual if Gushing Granny is used
                high_list.remove(value)

            # Send confirmation message
            user_name = await self.client.fetch_user(ctx.author.id)
            user_name = user_name.name

            if item.upper() == 'GUSHING GRANNY':
                gushing_used_title = f'{user_name} used Gushing Granny!'
                gushing_used_description = f'{target} is no longer high!'

                embed_gushing_used = discord.Embed(title=gushing_used_title, description=gushing_used_description, color=0xabcdef)
                await ctx.send(embed=embed_gushing_used)
            elif (item.upper() == 'CUM CHALICE') and (cum_check == 2):
                cum_used_title = f'{user_name} used Cum Chalice!'
                cum_used_description = f'Success: {target} swallowed it without thinking!\nThey are no longer high!'

                embed_cum_used = discord.Embed(title=cum_used_title, description='', color=0xabcdef)
                embed_cum_used.add_field(name='50% Check', value=cum_used_description, inline=False)
                await ctx.send(embed=embed_cum_used)
            else:
                cum_failed_title = f'{user_name} used Cum Chalice!'
                cum_failed_description = f'Failed: {target} reflexively spat it out!\nThe Cum Chalice has no effect on them!'

                embed_cum_failed = discord.Embed(title=cum_failed_title, description='', color=0xff0000)
                embed_cum_failed.add_field(name='50% Check', value=cum_failed_description, inline=False)
                await ctx.send(embed=embed_cum_failed)

            used += 1
        
        elif item.upper() == 'CONDUIT':
            if not target:
                target_id = ctx.author.id
                target = f'<@{ctx.author.id}>'
            else:
                target_id = int(target[2 : -1])  # Slice target user ID from ping

            target_exist = 0
            for i in range(len(lb)):
                if lb[i]['id'] == target_id:
                    target_exist += 1
                    break
            
            if target_exist == 0:
                await ctx.send('Invalid target!')
            
            # Check if target is protected already
            if target_id in conduit_list:
                await ctx.send('Target already has Conduit applied!')
                return
            
            # Add target to conduit list
            conduit_list.append(target_id)

            # Send confirmation message
            user_name = await self.client.fetch_user(ctx.author.id)
            user_name = user_name.name

            conduit_used_title = f'{user_name} used Conduit!'
            conduit_used_desc = f'{target} now has Conduit Power!'

            embed_conduit_used = discord.Embed(title=conduit_used_title, description=conduit_used_desc, color=0xabcdef)
            await ctx.send(embed=embed_conduit_used)

            used += 1
        
        elif item.upper() == 'TRAIN TICKET':
            user_id = ctx.author.id

            scenario_check = random.randint(0, len(scenarios) - 1)

            if scenarios[scenario_check]['name'] =='Cult Ritual':
                # Deduct 5 Gold Ingots
                for e in range(len(lb)):
                    if lb[e]['id'] == user_id:
                        if lb[e]['inventory']['Gold Ingot'] >= 5:  # Deduct all gold in inventory if user has less than 5 gold
                            lb[e]['inventory']['Gold Ingot'] -= 5
                        else:
                            lb[e]['inventory']['Gold Ingot'] = 0

                        break
                
            elif scenarios[scenario_check]['name'] == 'Amazon Warehouse':
                # Add 1 1984
                for f in range(len(lb)):
                    if lb[f]['id'] == user_id:
                        if 'Nineteen Eighty-Four' not in lb[f]['inventory']:
                            lb[f]['inventory']['Nineteen Eighty-Four'] = 1
                        else:
                            lb[f]['inventory']['Nineteen Eighty-Four'] += 1
                        
                        break
            
            elif scenarios[scenario_check]['name'] == 'Mine':
                # Add 5 amethyst shards
                for g in range(len(lb)):
                    if lb[g]['id'] == user_id:
                        if 'Amethyst Shard' not in lb[g]['inventory']:
                            lb[g]['inventory']['Amethyst Shard'] = 5
                        else:
                            lb[g]['inventory']['Amethyst Shard'] += 5
                        
                        break
            
            # Remove item from user's inventory if count is 0
            for h in range(len(lb)):
                if lb[h]['id'] == user_id:
                    for key, value in list(lb[h]['inventory'].items()):
                        if (key != 'Gold Ingot') and (key != 'Amethyst') and (value == 0):
                            del lb[h]['inventory'][key]
            
            # Send confirmation message
            await ctx.send('You used the ticket and got on the train.\nIt went to:')

            destination = scenarios[scenario_check]['name']

            scenario_num = scenario_check + 1
            scenario_desc = f'Destination #{scenario_num}'

            scenario_field = scenarios[scenario_check]['description']
            scenario_image = scenarios[scenario_check]['image']
            scenario_result = scenarios[scenario_check]['result']

            embed_ticket = discord.Embed(title=destination, description=scenario_desc, color=0xabcdef)

            embed_ticket.add_field(name='\u200b', value=scenario_field, inline=False)
            embed_ticket.set_image(url=scenario_image)
            embed_ticket.add_field(name='Result', value=scenario_result, inline=False)

            await ctx.send(embed=embed_ticket)

            used += 1

        else:
            await ctx.send('Item is unusable!')

        # Confirm spend item after using
        # Write changes to leaderboard
        if used == 1:
            outfile = open('data/pointless_leaderboard.json', 'w', encoding='utf-8')
            json.dump(lb, outfile, indent = 4)

# Setup function
async def setup(client):
    await client.add_cog(PointlessCog(client))   