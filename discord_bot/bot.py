import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import aiohttp
import requests
import logging


logging.basicConfig(level=logging.INFO)

# Load the environment variables
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_URL = os.getenv('API_URL')
GET_CARD = os.getenv('GET_CARD')
GET_COLLECTION = os.getenv('GET_COLLECTION')
UPDATE_COLLECTION = os.getenv('UPDATE_COLLECTION')
CREATE_USER = os.getenv('CREATE_USER')
PING_API = os.getenv('PING_API')

prompt_message_ids = {}


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


# Task to keep the bot alive
@tasks.loop(seconds=60)
async def keep_alive():
    try:
        requests.post(f"{API_URL}{PING_API}")
    except Exception as e:
        logging.error(f'Error sending ping: {e}')


# Create an embed message with the card details
async def create_embed(finish_interaction, chosen_card, chosen_finish, users):
    # Check if the card has two faces
    card_face1 = chosen_card
    card_face2 = None
    if "image_uris" not in chosen_card:
        if "card_faces" in chosen_card:
            card_face1 = chosen_card.get('card_faces')[0]
            card_face2 = chosen_card.get('card_faces')[1]

    price_key = None
    if chosen_finish == 'nonfoil':
        price_key = 'usd'
    elif chosen_finish == 'foil':
        price_key = 'usd_foil'
    elif chosen_finish == 'etched':
        price_key = 'usd_etched'

    embed1 = discord.Embed(title=card_face1.get('name'))
    embed1.set_image(url=card_face1.get('image_uris').get('normal'))

    embed2 = None
    if card_face2:
        embed2 = discord.Embed(title=card_face2.get('name'))
        embed2.set_image(url=card_face2.get('image_uris').get('normal'))

    # Creates main embed with card details
    embed_main = discord.Embed(title=chosen_card.get('name'))
    embed_main.add_field(name="Set Name",
                         value=chosen_card.get('set_name'), inline=True)
    embed_main.add_field(name="Released At",
                         value=chosen_card.get('released_at'), inline=True)
    embed_main.add_field(name="Price (USD)",
                         value=f"${chosen_card.get('prices').get(price_key)}",
                         inline=True)
    embed_main.add_field(name="Collector Number",
                         value=f"{chosen_card.get('set').upper()} {chosen_card.get('collector_number')}", inline=True)
    embed_main.add_field(name="Finish",
                         value=chosen_finish.capitalize(), inline=True)

    # Create hyperlinks for TCGplayer, Scryfall, and EDHREC
    links = [
        f"* [TCGplayer]({chosen_card.get('purchase_uris').get('tcgplayer')})\n",
        f"* [Scryfall]({chosen_card.get('scryfall_uri')})\n",
        f"* [EDHREC]({chosen_card.get('related_uris').get('edhrec')})\n"
    ]
    linkList = ""
    for link in links:
        linkList += link
    embed_main.add_field(name="Links",
                         value=linkList, inline=True)

    # Create a list of users who own the card
    output = ""
    for key, value in users.items():
        output += f"__**{key}:**__\n"
        for ownedCard in value:
            card_link = f"https://www.tcgplayer.com/product/{ownedCard['tcg_id']}"
            output += f"* [{ownedCard['set']} {ownedCard['collector_number']}]({card_link})\n" \
                      f" * Finish: {ownedCard['finish'].capitalize()}\n * Price: ${ownedCard['price']}\n" \
                      f" * Quantity: {ownedCard['quantity']}\n"

    embed_main.add_field(name="Owners",
                         value=output, inline=True)

    if embed2:
        await finish_interaction.response.send_message(embeds=[embed_main, embed1, embed2])
    else:
        embed_main.set_image(url=chosen_card.get('image_uris').get('normal'))
        await finish_interaction.response.send_message(embed=embed_main)


# Command: /get_card <name>
@bot.tree.command(name='get_card', description='Get information about a Magic: The Gathering card')
async def card(interaction: discord.Interaction, name: str):
    response = requests.get(f"{API_URL}{GET_CARD}", params={'name': name, 'type': 'card'})
    if response.status_code == 200:
        card_data = response.json()
        user_list = card_data.get('users', [])
        finish = card_data.get('finishes', [])[0]
        await create_embed(interaction, card_data, finish, user_list)
    else:
        logging.error(f'Failed to retrieve card: {response.status_code}')
        await interaction.response.send_message('Failed to retrieve card.')


# Command: /get_printing <name>
@bot.tree.command(name='get_printing', description='Get a specific printing of a Magic: The Gathering card')
async def card(card_interaction: discord.Interaction, name: str):
    response = requests.get(f"{API_URL}{GET_CARD}", params={'name': name, 'type': 'printing'})
    if response.status_code == 200:
        card_data = response.json()
        set_list = card_data.get('prints', [])
        users = card_data.get('users', {})

        set_options = []
        for set_card in set_list:
            label = f"{set_card.get('set_name')} - {set_card.get('collector_number')}"
            value = f"{set_card.get('id')}"
            set_options.append(discord.SelectOption(label=label, value=value))

        # Function to create set select options
        def create_select_options(start_index):
            select_list = []
            for i in range(start_index, len(set_options)):
                select_list.append(set_options[i])
                if len(select_list) == 24:
                    select_list.append(discord.SelectOption(label="More...", value="more"))
                    return select_list
                elif i == len(set_options) - 1:
                    return select_list

        # Display the set options in a discord select menu
        async def display_options(interaction, start_index):
            select = discord.ui.Select(placeholder="Choose a printing", options=create_select_options(start_index))

            # Callback function for the select menu
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

                            # Callback function for the finish select menu
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
                                    await create_embed(finish_interaction, selected_card, selected_finish, users)
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

    else:
        logging.error(f'Failed to retrieve card: {response.status_code}')
        await card_interaction.response.send_message('Failed to retrieve card.')


# Command: /create_user
@bot.tree.command(name='create_user', description='Create a new user')
async def create_user(interaction: discord.Interaction):
    user_id = interaction.user.id
    username = interaction.user.name
    data = {
        'discord_id': user_id,
        'discord_username': username,
    }
    response = requests.post(f"{API_URL}{CREATE_USER}", json=data)
    if response.status_code == 201:
        await interaction.response.send_message('User created successfully!')
    else:
        await interaction.response.send_message('Failed to create user.')


# Command: /get_collection
@bot.tree.command(name='get_collection', description='Get your collection')
async def get_collection(interaction: discord.Interaction):
    user_id = interaction.user.id
    response = requests.get(f"{API_URL}{GET_COLLECTION}", params={'discord_id': user_id})
    if response.status_code == 200:
        collection = response.json()
        if collection:
            card_count = collection[0]['card_count']
            total_value = collection[0]['total_value']
            embed = discord.Embed(title=f"{interaction.user.name}'s Collection")
            embed.add_field(name="Card Count", value=card_count, inline=True)
            embed.add_field(name="Total Value", value=f"${total_value}", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message('No cards found in your collection.')
    else:
        await interaction.response.send_message('Failed to retrieve collection.')


# Command: /update_collection
@bot.tree.command(name="update_collection", description="Upload a CSV file to update your collection")
async def upload(interaction: discord.Interaction):
    await interaction.response.send_message("Please reply to this message with your CSV file attached.")
    message = await interaction.original_response()
    prompt_message_ids[interaction.user.id] = message.id


# Event listener for when a message is sent
@bot.event
async def on_message(message):
    # Check if the message is from the user who uploaded the CSV file
    user_id = message.author.id
    if user_id in prompt_message_ids:
        if message.attachments:
            if message.reference and message.reference.message_id:
                if message.reference.message_id == prompt_message_ids[user_id]:
                    for attachment in message.attachments:
                        if attachment.filename.endswith('.csv'):
                            async with aiohttp.ClientSession() as session:
                                async with session.get(attachment.url) as response:
                                    if response.status == 200:
                                        data = await response.read()
                                        form = aiohttp.FormData()
                                        form.add_field('file', data,
                                                       filename=attachment.filename, content_type='text/csv')
                                        form.add_field('action', 'add')
                                        form.add_field('discord_id', str(user_id))

                                        async with session.post(f'{API_URL}{UPDATE_COLLECTION}',
                                                                data=form) as api_response:
                                            if api_response.status == 200:
                                                await message.channel.send(
                                                    f"CSV file '{attachment.filename}' uploaded successfully!")
                                            else:
                                                await message.channel.send(
                                                    f"Failed to upload CSV file '{attachment.filename}'")

                            del prompt_message_ids[user_id]


# Command: /hello
@bot.tree.command(name='hello', description='Say hello!')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)
