import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

bot = commands.Bot(command_prefix='!')


# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


# Command: !hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')

# Run the bot
bot.run(BOT_TOKEN)
