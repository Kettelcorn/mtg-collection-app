import discord
import subprocess
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import requests
import logging
import asyncio
from cards.scryfall_bulk import fetch_bulk_data_list, get_bulk_data_download_uri, download_bulk_data, process_bulk_data


logging.basicConfig(level=logging.INFO)

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


@tasks.loop(seconds=10)  # Change the interval to 30 seconds
async def keep_alive():
    try:
        # Perform an internal operation to keep the bot's connection alive
        await bot.ws.ping()
        print("Sent keep-alive ping")
    except Exception as e:
        print(f"Error sending keep-alive ping: {e}")

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
    await ctx.send("Updating your cards... :hourglass:")

    async def run_update():
        try:
            download_uri, total_size = get_bulk_data_download_uri("default_cards")
            if not download_uri:
                logging.error('Failed to get download URI')
                await ctx.send('Failed to get download URI')
                return
            downloaded_data = await download_bulk_data(download_uri, total_size)
            if downloaded_data:
                await ctx.send("Cards updated successfully.")
            else:
                await ctx.send("Failed to update cards. Download aborted.")
        except Exception as e:
            logging.error(f'Error during update: {e}')
            await ctx.send(f'Failed to update cards: {e}')

    await asyncio.create_task(run_update())



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

