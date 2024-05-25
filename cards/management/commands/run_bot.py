from django.core.management.base import BaseCommand
import discord
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

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

logging.info("All environment variables are set.")


# Function to retrieve access token
def get_access_token():
    try:
        response = requests.post(API_TOKEN_URL, data={
            'username': API_USERNAME,
            'password': API_PASSWORD
        })
        response.raise_for_status()
        logging.info("Access token retrieved successfully.")
        return response.json()['access']
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to retrieve access token: {e}')
        exit(1)


# Retrieve the initial access token
access_token = get_access_token()

# Define intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)


# Event listener for when the bot is ready
@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')


# Command: !card <name>
@bot.command(name='card')
async def card(ctx, *, name: str):
    global access_token
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


class Command(BaseCommand):
    help = 'Run the Discord bot'

    def handle(self, *args, **options):
        try:
            bot.run(BOT_TOKEN)
        except discord.errors.LoginFailure as e:
            logging.error(f'Failed to log in: {e}')
            exit(1)
