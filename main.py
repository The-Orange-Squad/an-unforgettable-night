import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord.ui import Button, View
from dotenv import load_dotenv
import os
import random
import asyncio
import json

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

infected_id = None
guesses_left = 3
transfer_flasher = False
verified_member_role_id = 1080481494453190726  # Replace with your verified member role ID

# User stats dictionary
user_stats = {}

@bot.event
async def on_message(message):
	if message.channel.id == 1168948527687286794:
		role_id = 1168955242474377297  # Replace with your role ID
		role = message.guild.get_role(role_id)
		# Check if the message is sent in the "selected" channel
		if role and message.content != role.mention:
			await message.channel.send(role.mention)

def load_stats():
    global user_stats
    try:
        with open('user_stats.json', 'r') as f:
            user_stats = json.load(f)
            # convert all user ids to ints
            user_stats = {int(user_id): stats for user_id, stats in user_stats.items()}
    except FileNotFoundError:
        pass

def save_stats():
    with open('user_stats.json', 'w') as f:
        json.dump(user_stats, f)

def update_stat(user_id, stat, increment=1):
    if user_id not in user_stats:
        user_stats[user_id] = {
            'Lost as Infected': 0,
            'Won as Infected': 0,
            'Lost as Guesser': 0,
            'Won as Guesser': 0,
            'Searches Made': 0,
            'Guesses Made': 0,
            'Successful Guess Rate': 0.0,
        }
    user_stats[user_id][stat] += increment
    if stat == 'Guesses Made':
        successful_guesses = user_stats[user_id]['Won as Guesser']
        total_guesses = user_stats[user_id]['Guesses Made']
        user_stats[user_id]['Successful Guess Rate'] = successful_guesses / total_guesses if total_guesses > 0 else 0.0
    if stat == "Won as Guesser":
        successful_guesses = user_stats[user_id]['Won as Guesser']
        total_guesses = user_stats[user_id]['Guesses Made']
        user_stats[user_id]['Successful Guess Rate'] = successful_guesses / total_guesses if total_guesses > 0 else 0.0
    save_stats()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    load_stats()
    await select_infected()

# Transfer button
class TransferButton(discord.ui.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == infected_id:
            embed = discord.Embed(title="Error", description="You are not infected.", color=0xFF5733)
            await interaction.response.send_message(embed=embed)
            return
        
        mod = bot.get_user(861620168370683924)
        await mod.send(f"Transfer request: {interaction.user.name}")
        
        global transfer_flasher
        transfer_flasher = True
        embed = discord.Embed(title="🔄 Transferred", description="The Infected user has transferred the infection to someone else.", color=discord.Colour.blue())
        await bot.get_channel(1168948527687286794).send(embed=embed)
        embed = discord.Embed(title="🔄 Transferred", description="You have transferred the infection to someone else.", color=discord.Colour.blue())
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(1)
        guesses_left = 3
        await select_infected()

# Transfer view
class TransferView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TransferButton(label="Transfer", style=discord.ButtonStyle.blurple))

async def select_infected():
    global infected_id
    global transfer_flasher
    while True:
        guild = bot.get_guild(1079761115636043926)  # replace with your guild id
        members = [member for member in guild.members if not member.bot]
        infected_member = random.choice(members)
        infected_id = infected_member.id
        embed = discord.Embed(title="🦠 You are infected!", description="You have been infected with the MoneyVirus. Now people will try to uncover your identity. If they guess it correctly, you will be cured. If not, you will win.", color=discord.Colour.green())
        embed.set_footer(text="This message is sent from The Orange Squad. If you don't want to participate, please transfer.")
        verified_member_role = guild.get_role(verified_member_role_id)
        if verified_member_role not in infected_member.roles:
            await select_infected()
            return
        try:
            await infected_member.send(embed=embed, view=TransferView())
        except:
            await select_infected()
            return
        channel = bot.get_channel(1168948527687286794)  # replace with your channel id
        embed2 = discord.Embed(title="🔍 Someone has been infected!", description=f"A random member has been infected with the MoneyVirus. Try to find out who it is! You have 3 guesses. If you guess correctly, the infected person will be cured. If not, the infected person will win.", color=discord.Colour.red())
        await channel.send(embed=embed2)
        
        # Send a message to the mod (by ID) to notify them of the new infected
        mod = bot.get_user(861620168370683924)
        await mod.send(f"New infected: {infected_member.name}")
        
        for i in range(3600):
            if transfer_flasher:
                transfer_flasher = False
                return
            
            await asyncio.sleep(1)
        
        if infected_id:
            # If the infected member hasn't been guessed in an hour, they win automatically
            update_stat(infected_id, 'Won as Infected')
            embed = discord.Embed(title="🎉 Infected Wins!", description=f"The infected person ({infected_member.mention}) has won since they weren't guessed in an hour.", color=discord.Colour.gold())
            await channel.send(embed=embed)
            infected_id = None

@bot.slash_command(name='search', description='Search for a pattern')
@commands.cooldown(1, 10, commands.BucketType.guild)
async def search(ctx, pattern: Option(str, 'Enter the pattern')):
    """
    Search for a pattern in the guild members and return the percentage of infected members that match the pattern.
    """
    update_stat(ctx.author.id, 'Searches Made')
    guild = bot.get_guild(1079761115636043926)  # replace with your guild id
    matching_members = [member for member in guild.members if not member.bot and pattern.lower() in member.name.lower()]
    infected_members = [member for member in matching_members if member.id == infected_id]
    num_matching_members = len(matching_members)
    num_infected_members = len(infected_members)
    
    if num_matching_members > 0:
        # Get the percentage of infected members that match the pattern
        percentage = num_infected_members / num_matching_members
        # Set the emoji based on the percentage
        if percentage == 0:
            emoji = "🟦"
        elif percentage <= 0.1:
            emoji = "🟩"
        elif percentage <= 0.25:
            emoji = "🟨"
        elif percentage <= 0.35:
            emoji = "🟧"
        else:
            emoji = "🟥"
    else:
        percentage = 0
        emoji = "🟦"
    
    # Show the percentage, the emoji, and the matching members
    members_string = '\n'.join([member.mention for member in matching_members])
    embed = discord.Embed(title="🔍 Search Results", description=f"**Percentage:** {percentage:.2%} {emoji}\n**Matching Members:**\n{members_string}", color=0xFF5733)
    
    # Set the color of the embed based on the percentage
    if percentage == 0:
        embed.color = 0x0000FF
    elif percentage <= 0.1:
        embed.color = discord.Colour.green()
    elif percentage <= 0.25:
        embed.color = discord.Colour.gold()
    elif percentage <= 0.35:
        embed.color = discord.Colour.orange()
    else:
        embed.color = discord.Colour.red()

    await ctx.respond(embed=embed)

# Cooldown error handler
@search.error
async def search_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Error", description=f"Please wait {error.retry_after:.2f} seconds before using this command again.", color=0xFF5733)
        await ctx.respond(embed=embed)
    else:
        raise error

@bot.slash_command(name='guess', description='Guess the infected person')
async def guess(ctx, member: Option(discord.Member, 'Enter the member')):
    global infected_id, guesses_left, transfer_flasher
    
    if not infected_id:
        embed = discord.Embed(title="Error", description="There is no infected person right now.", color=0xFF5733)
        await ctx.respond(embed=embed)
        return
    
    if guesses_left == 0:
        embed = discord.Embed(title="Error", description="No more guesses left.", color=0xFF5733)
        await ctx.respond(embed=embed)
        return

    update_stat(ctx.author.id, 'Guesses Made')    
    if member.id == infected_id:
        update_stat(ctx.author.id, 'Won as Guesser')
        update_stat(infected_id, 'Lost as Infected')
        
        embed = discord.Embed(title="🎉 Congratulations!", description=f"You found the infected person. You win!", color=discord.Colour.blurple())
        await ctx.respond(embed=embed)
        
        embed = discord.Embed(title="💔 Defeat", description=f"{ctx.author.mention} found you.", color=0xFF5733)
        await member.send(embed=embed)
        
        embed = discord.Embed(title="🏥 Cured", description="You are not infected anymore.", color=discord.Colour.blue())
        await member.send(embed=embed)
        
        infected_id = None
        guesses_left = 3
        transfer_flasher = True
        await asyncio.sleep(1)
        transfer_flasher = False
        await select_infected()
    else:
        guesses_left -= 1
        
        if guesses_left > 0:
            embed = discord.Embed(title="Error", description=f"Sorry {ctx.author.mention}, your guess is incorrect. {guesses_left} guess(es) left.", color=discord.Colour.orange())
            await ctx.respond(embed=embed)
        else:
            update_stat(ctx.author.id, 'Lost as Guesser')
            update_stat(infected_id, 'Won as Infected')
            
            embed = discord.Embed(title="😔 Sorry", description=f"Your guess is incorrect. The infected person wins!\n\nThe infected person was {bot.get_user(infected_id).mention}.", color=discord.Colour.red())
            await ctx.respond(embed=embed)
            
            infected_member = bot.get_user(infected_id)
            embed = discord.Embed(title="🎉 Victory", description="You won!", color=discord.Colour.gold())
            await infected_member.send(embed=embed)
            
            embed = discord.Embed(title="🏥 Cured", description="You are not infected anymore.", color=discord.Colour.blue())
            await infected_member.send(embed=embed)
            
            infected_id = None
            guesses_left = 3
            
            transfer_flasher = True
            await asyncio.sleep(1)
            transfer_flasher = False
            await select_infected()

@bot.slash_command(name='help', description='Explain the rules of the game')
async def help(ctx):
    """
    This command explains the rules of the game.
    """
    embed = discord.Embed(title="📚 Rules of the Game", color=discord.Colour.green())
    embed.add_field(name="Objective", value="A random member is infected with the MoneyVirus. The goal is to find out who it is. If the infected person is guessed correctly, they will be cured. If not, they will win.", inline=False)
    embed.add_field(name="Commands", value="Use `/search` to search for a pattern in the guild members and return the percentage of infected members that match the pattern. Use `/guess` to guess who the infected person is.", inline=False)
    embed.add_field(name="Transfer", value="The infected person can transfer the infection to someone else by clicking on the 'Transfer' button.", inline=False)
    embed.add_field(name="Winning", value="If the infected person isn't guessed within an hour, they win automatically.", inline=False)
    # A new embed to explain all the commands (use a package emoji)
    embed2 = discord.Embed(title=":package: Commands", color=discord.Colour.green())
    embed2.add_field(name="/search", value="Search for a pattern in the guild members and return the percentage of infected members that match the pattern. The guild is the server that the bot is in. The percentage is based on the number of infected members that match the pattern divided by 1, the infected member. The percentage is rounded to 2 decimal places.", inline=False)
    embed2.add_field(name="/guess", value="Guess who the infected person is. If you guess correctly, the infected person will be cured. If not, the infected person will win.", inline=False)
    embed2.add_field(name="/help", value="Explain the rules of the game.", inline=False)
    embed2.add_field(name="/ping", value="Get the bot latency.", inline=False) 
    embed2.add_field(name="/user_stats", value="View your stats, or the stats of another user.\n**The stats are:**\n- Lost as Infected\n- Won as Infected\n- Lost as Guesser\n- Won as Guesser\n- Searches Made\n- Guesses Made\n- Successful Guess Rate", inline=False)
    await ctx.respond(embed=embed)
    await ctx.respond(embed=embed2)

@bot.slash_command(name='ping', description='Get the bot latency')
async def ping(ctx):
    """
    This command returns the bot latency.
    """
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: {bot.latency * 1000:.2f} ms", color=discord.Colour.red())
    await ctx.respond(embed=embed)

@bot.slash_command(name='user_stats', description='View user stats')
async def userstats(ctx, user: Option(discord.User, 'Enter the user')):
    """
    This command shows the stats of a user.
    """
    user_id = user.id
    if user_id not in user_stats:
        embed = discord.Embed(title=f"{user.name}'s Stats", description="No stats available.", color=discord.Colour.red())
        await ctx.respond(embed=embed)
        return
    stats = user_stats[user_id]
    
    embed = discord.Embed(title=f"{user.name}'s Stats", color=discord.Colour.blue())
    
    for stat, value in stats.items():
        if stat == 'Successful Guess Rate':
            value = f"{value:.2%}"
        embed.add_field(name=stat, value=value, inline=False)
    
    await ctx.respond(embed=embed)

bot.run(token)
