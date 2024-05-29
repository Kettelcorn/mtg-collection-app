import discord
import subprocess
from discord.ext import commands, tasks
from discord import app_commands
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
    await bot.tree.sync()
    print(f'{bot.user} has connected to Discord!')
    keep_alive.start()


@tasks.loop(seconds=10)
async def keep_alive():
    try:
        await bot.http.get_gateway()
        result = subprocess.run(['python', 'manage.py', 'keep_alive'], capture_output=True, text=True)
        logging.info("Sent keep-alive request")
    except Exception as e:
        logging.error(f'Error sending keep-alive request: {e}')



# Command: !card <name>
@bot.tree.command(name='card', description='Get information about a Magic: The Gathering card')
async def card(interaction: discord.Interaction, name: str):
    params = {
        'fuzzy': name
    }
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        try:
            card = response.json()
            logging.info(f'Parsed JSON response: {card}')
            if card.get('object') == 'error':
                await interaction.response.send_message("No card found.")
            else:
                response = requests.get(card.get('prints_search_uri'))
                if response.status_code == 200:
                    set_list = response.json().get('data')
                    set_options = [discord.SelectOption(
                        label=f"{set_card.get('set_name')} - {set_card.get('collector_number')} - {'foil' if 'foil' in set_card.get('finishes') else 'nonfoil'}",
                        value=set_card.get('id'))
                                   for set_card in set_list]

                    def create_select_options(start_index):
                        select_list = []
                        for i in range(start_index, len(set_options)):
                            select_list.append(set_options[i])
                            if len(select_list) == 24:
                                select_list.append(discord.SelectOption(label="More...", value="more"))
                                return select_list
                            elif i == len(set_options) - 1:
                                return select_list
                    select = discord.ui.Select(placeholder="Choose a printing", options=create_select_options(0))

                    async def select_callback(interaction: discord.Interaction):
                        selected_value = interaction.data.get('values')[0]
                        if selected_value == "more":
                            next_options = create_select_options(24)
                            next_select = discord.ui.Select(placeholder="Choose a printing", options=next_options)

                            async def next_select_callback(interaction):
                                next_selected_value = interaction.data.get('values')[0]
                                if next_selected_value == "more":
                                    await interaction.response.send_message("No more options available.")
                                    return
                                select_card = None
                                for set_card in set_list:
                                    if set_card.get('id') == next_selected_value:
                                        select_card = set_card
                                        break
                                embed = discord.Embed(title=select_card.get('name'),
                                                      description=select_card.get('oracle_text'))
                                embed.add_field(name="Mana Cost", value=select_card.get('mana_cost'), inline=True)
                                embed.add_field(name="CMC", value=select_card.get('cmc'), inline=True)
                                embed.add_field(name="Type", value=select_card.get('type_line'), inline=True)
                                embed.add_field(name="Rarity", value=select_card.get('rarity'), inline=True)
                                embed.add_field(name="Set Name", value=select_card.get('set_name'), inline=True)
                                embed.add_field(name="Released At", value=select_card.get('released_at'), inline=True)
                                embed.add_field(name="Price (USD)", value=f"${select_card.get('prices').get('usd')}",
                                                inline=True)
                                embed.set_image(url=select_card.get('image_uris').get('normal'))
                                await interaction.response.send_message(embed=embed)

                            next_select.callback = next_select_callback
                            next_view = discord.ui.View()
                            next_view.add_item(next_select)
                            await interaction.response.send_message("Choose a printing:", view=next_view, ephemeral=True)
                        else:
                            for set_card in set_list:
                                if set_card.get('id') == selected_value:
                                    selected_card = set_card
                                    break
                            embed = discord.Embed(title=selected_card.get('name'),
                                                  description=selected_card.get('oracle_text'))
                            embed.add_field(name="Mana Cost", value=selected_card.get('mana_cost'), inline=True)
                            embed.add_field(name="CMC", value=selected_card.get('cmc'), inline=True)
                            embed.add_field(name="Type", value=selected_card.get('type_line'), inline=True)
                            embed.add_field(name="Rarity", value=selected_card.get('rarity'), inline=True)
                            embed.add_field(name="Set Name", value=selected_card.get('set_name'), inline=True)
                            embed.add_field(name="Released At", value=selected_card.get('released_at'), inline=True)
                            embed.add_field(name="Price (USD)", value=f"${selected_card.get('prices').get('usd')}",
                                            inline=True)
                            embed.set_image(url=selected_card.get('image_uris').get('normal'))
                            await interaction.response.send_message(embed=embed)

                    select.callback = select_callback
                    view = discord.ui.View()
                    view.add_item(select)
                    await interaction.response.send_message("Choose a printing:", view=view, ephemeral=True)
        except ValueError:
            logging.error('Failed to parse JSON response')
            await interaction.response.send_message('Failed to parse response from server.')
    else:
        logging.error(f'Failed to retrieve card: {response.status_code}')
        await interaction.response.send_message('Failed to retrieve card.')


async def run_update(ctx):
    try:
        # Run synchronous code in a separate thread
        download_uri, total_size = await asyncio.to_thread(get_bulk_data_download_uri, "default_cards")
        if not download_uri:
            logging.error('Failed to get download URI')
            await ctx.send('Failed to get download URI')
            return

        # Run synchronous download in a separate thread
        downloaded_data = await asyncio.to_thread(download_bulk_data, download_uri, total_size)
        if downloaded_data:
            await ctx.send("Cards updated successfully.")
        else:
            await ctx.send("Failed to update cards. Download aborted.")
    except Exception as e:
        logging.error(f'Error during update: {e}')
        await ctx.send(f'Failed to update cards: {e}')


# Command: !update_cards
@bot.command(name='update_cards')
async def update_cards(ctx):
    await ctx.defer()
    await ctx.send("Updating your cards... :hourglass:")
    asyncio.create_task(run_update(ctx))


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
@bot.tree.command(name='hello', description='Say hello!')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)