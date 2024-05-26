import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import logging

# logging.basicConfig(level=logging.INFO)

# Load the environment variables
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_URL = os.getenv('API_URL')


# Define intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)


# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


# Command: !card <name>
@bot.command(name='card')
async def card(ctx, *, name: str):
    params = {
        'name': name
    }
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        try:
            card = response.json()
            logging.info(f'Parsed JSON response: {card}')
            if 'error' in card:
                await ctx.send(card['error'])
            else:
                await ctx.send(
                    f"Name: {card['name']}\nStats: {card['stats']}\nDescription: {card['description']}\nPrice: {card['price']}")
        except ValueError:
            logging.error('Failed to parse JSON response')
            await ctx.send('Failed to parse response from server.')
    else:
        await ctx.send('Failed to retrieve card.')


# Command: !hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)

