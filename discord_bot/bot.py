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
async def card(card_interaction: discord.Interaction, name: str):
    params = {
        'fuzzy': name
    }
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        try:
            card = response.json()
            if card.get('object') == 'error':
                await card_interaction.response.send_message("No card found.")
            else:
                response = requests.get(card.get('prints_search_uri'))
                if response.status_code == 200:
                    set_list = response.json().get('data')
                    set_options = []
                    for set_card in set_list:
                        label = f"{set_card.get('set_name')} - {set_card.get('collector_number')}"
                        value = f"{set_card.get('id')}"
                        set_options.append(discord.SelectOption(label=label, value=value))

                    def create_select_options(start_index):
                        select_list = []
                        for i in range(start_index, len(set_options)):
                            select_list.append(set_options[i])
                            if len(select_list) == 24:
                                select_list.append(discord.SelectOption(label="More...", value="more"))
                                return select_list
                            elif i == len(set_options) - 1:
                                return select_list

                    async def display_options(interaction, start_index):
                        select = discord.ui.Select(placeholder="Choose a printing", options=create_select_options(start_index))

                        async def select_callback(set_interaction: discord.Interaction):
                            selected_value = set_interaction.data.get('values')[0]
                            if selected_value == "more":
                                await display_options(set_interaction, start_index + 24)
                            else:
                                selected_card = None
                                for select_card in set_list:
                                    if f"{select_card.get('id')}" == selected_value:
                                        selected_card = select_card
                                        finished = []
                                        for finish in selected_card.get('finishes'):
                                            finished.append(discord.SelectOption(label=f"{finish.capitalize()}",
                                                                                 value=f"{finish}"))

                                        finish_select = discord.ui.Select(placeholder="Choose a finish",
                                                                          options=finished)

                                        async def create_embed(finish_interaction, chosen_card, chosen_finish):
                                            chosen_finish = finish_interaction.data.get('values')[0]
                                            embed = discord.Embed(title=chosen_card.get('name'),
                                                                  description=chosen_card.get('oracle_text'))
                                            embed.add_field(name="Mana Cost",
                                                            value=chosen_card.get('mana_cost'), inline=True)
                                            embed.add_field(name="CMC",
                                                            value=chosen_card.get('cmc'), inline=True)
                                            embed.add_field(name="Type",
                                                            value=chosen_card.get('type_line'), inline=True)
                                            embed.add_field(name="Rarity",
                                                            value=chosen_card.get('rarity'), inline=True)
                                            embed.add_field(name="Set Name",
                                                            value=chosen_card.get('set_name'), inline=True)
                                            embed.add_field(name="Released At",
                                                            value=chosen_card.get('released_at'), inline=True)
                                            price_key = 'usd_foil' if chosen_finish == 'foil' else 'usd'
                                            embed.add_field(name="Price (USD)",
                                                            value=f"${chosen_card.get('prices').get(price_key)}",
                                                            inline=True)
                                            embed.set_image(url=chosen_card.get('image_uris').get('normal'))
                                            await finish_interaction.response.send_message(embed=embed)

                                        async def select_finish(finish_interaction):
                                            selected_finish = None
                                            chosen_finish = finish_interaction.data.get('values')[0]
                                            for each_finish in selected_card.get('finishes'):
                                                if f"{each_finish}" == chosen_finish:
                                                    selected_finish = each_finish
                                                    logging.info(f"Selected finish: {selected_finish}")
                                                    break
                                            if selected_finish:
                                                logging.info(f"Creating embed for finish: {selected_finish}")
                                                await create_embed(finish_interaction, selected_card, selected_finish)
                                            else:
                                                logging.error(f"Failed to select finish: {chosen_finish}")
                                                await finish_interaction.response.send_message("Failed to select finish.")

                                        finish_select.callback = select_finish
                                        finish_view = discord.ui.View()
                                        finish_view.add_item(finish_select)
                                        await set_interaction.response.send_message("Choose a finish:",
                                                                                    view=finish_view,
                                                                                    ephemeral=True)

                        select.callback = select_callback
                        view = discord.ui.View()
                        view.add_item(select)
                        await interaction.response.send_message("Choose a printing:", view=view, ephemeral=True)

                    await display_options(card_interaction, 0)
        except ValueError:
            logging.error('Failed to parse JSON response')
            await card_interaction.response.send_message('Failed to parse response from server.')
    else:
        logging.error(f'Failed to retrieve card: {response.status_code}')
        await card_interaction.response.send_message('Failed to retrieve card.')


# Command: !hello
@bot.tree.command(name='hello', description='Say hello!')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)