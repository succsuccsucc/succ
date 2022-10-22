# succ.py
# cog for ?succ command
import discord
from discord.ext import commands
import os

# Change working directory to wherever this file is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class SuccCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def succ(self, ctx):
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
        content = ''  # Copy message content
        if succ_msg.content == '':
            content = 'Message content is empty!'
        else:
            content = succ_msg.content
        
        sender_id = succ_msg.author.id  # Copy message sender
        sender_ping = f'<@{sender_id}>'

        embed_succ = discord.Embed(title='Slurp!', description='Your message got succ\'d', color=0xabcdef)
        embed_succ.add_field(name='Sender', value=sender_ping, inline=False)
        embed_succ.add_field(name='Message', value=content, inline=False)  
        await ctx.channel.send(embed=embed_succ)
        await succ_msg.delete()  # Delete the 2nd last message
        return
    
# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class
# When we load the cog, we use the name of the file.
async def setup(client):
    await client.add_cog(SuccCog(client))