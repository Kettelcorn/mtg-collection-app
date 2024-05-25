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
API_USERNAME = os.getenv('API_USERNAME')
API_PASSWORD = os.getenv('API_PASSWORD')
API_URL = os.getenv('API_URL')
API_TOKEN_URL = os.getenv('API_TOKEN_URL')

if not all([BOT_TOKEN, API_USERNAME, API_PASSWORD, API_URL, API_TOKEN_URL]):
    logging.error('One or more environment variables are missing.')
    exit(1)


# Function to retrieve access token
def get_access_token():
    response = requests.post(API_TOKEN_URL, data={
        'username': API_USERNAME,
        'password': API_PASSWORD
    })
    response.raise_for_status()
    return response.json()['access']


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
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'name': name
    }
    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 401:
        access_token = get_access_token()
        headers['Authorization'] = f'Bearer {access_token}'
        response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 200:
        cards = response.json()
        if cards:
            for item in cards:
                await ctx.send(
                    f"Name: {item['name']}\nStats: {item['stats']}\nDescription: {item['description']}\nPrice: {item['price']}")
        else:
            await ctx.send('No cards found with that name.')
    else:
        await ctx.send('Failed to retrieve cards.')


# Command: !hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)

