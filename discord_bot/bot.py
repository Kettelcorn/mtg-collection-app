import discord
import subprocess
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import logging
import threading

# logging.basicConfig(level=logging.INFO)

# Load the environment variables
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_URL = os.getenv('API_URL')
UPDATE_URL = os.getenv('UPDATE_URL')


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
            cards = response.json()
            logging.info(f'Parsed JSON response: {cards}')
            if not cards:
                await ctx.send('No card found.')
            else:
                for card in cards:
                    embed = discord.Embed(title=card.get('name'), description=card.get('description'))
                    embed.add_field(name="Power", value=card.get('power'), inline=True)
                    embed.add_field(name="Toughness", value=card.get('toughness'), inline=True)
                    embed.add_field(name="Colors", value=card.get('colors'), inline=True)
                    embed.add_field(name="Rarity", value=card.get('rarity'), inline=True)
                    embed.add_field(name="Set Name", value=card.get('set_name'), inline=True)
                    embed.add_field(name="Price", value=f"${card.get('price')}", inline=True)
                    embed.set_image(url=card.get('image_url'))
                    await ctx.send(embed=embed)
        except ValueError:
            logging.error('Failed to parse JSON response')
            await ctx.send('Failed to parse response from server.')
    else:
        logging.error(f'Failed to retrieve card: {response.status_code}')
        await ctx.send('Failed to retrieve card.')


# Command: !update_cards
@bot.command(name='update_cards')
async def update_cards(ctx):
    await ctx.defer()
    try:
        await ctx.send("Updating your cards... :hourglass:")
        response = requests.post(UPDATE_URL)
        if response.status_code == 200:
            await ctx.send("Cards updated successfully.")
        else:
            await ctx.send(f"Failed to update cards. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error updating cards: {e}")
        await ctx.send(f"Error updating cards: {e}")


# Command: !count_cards
@bot.command(name='count_cards')
async def count_cards(ctx):
    try:
        result = subprocess.run(['python', 'manage.py', 'count_cards'], capture_output=True, text=True)
        if result.returncode == 0:
            await ctx.send(result.stdout)
        else:
            await ctx.send(f'Error: {result.stderr}')
    except Exception as e:
        await ctx.send(f'Error: {e}')


# Command: !hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)

