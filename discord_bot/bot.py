import discord
from discord import Intents, interactions, ui
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import aiohttp
import requests
import logging
import jwt
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

intents = Intents.default()
intents.members = True

# Load the environment variables
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_URL = os.getenv('API_URL')
OAUTH_URL = os.getenv('OAUTH_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

prompt_message_ids = {}


user_tokens = {}


# Define intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)


async def get_valid_users(guild):
    await guild.chunk()
    users = guild.members
    valid_users = []
    for user in users:
        valid_users.append(user.name)
    return valid_users


# Event listener for when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()
    keep_alive.start()


# Task to keep the bot alive
@tasks.loop(seconds=60)
async def keep_alive():
    try:
        requests.post(f"{API_URL}/api/ping/")
    except Exception as e:
        logger.error(f'Error sending ping: {e}')


def fetch_tokens(username):
    response = requests.get(f"{API_URL}/api/fetch_tokens/", params={'username': username, 'jwt_secret': JWT_SECRET},)
    if response.status_code == 200:
        tokens = response.json()
        logger.info(f"Fetched tokens: {tokens}")
        # Decode the access token to get the expiration time
        access_token_decoded = jwt.decode(tokens['access_token'], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        logger.info(f"Decoded token: {access_token_decoded}")
        expiration_time = datetime.fromtimestamp(access_token_decoded['exp'])
        user_tokens[username] = {
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'expires_at': expiration_time
        }
        return tokens
    else:
        logger.error(f"Failed to fetch tokens: {response.status_code} - {response.text}")
        return None


def refresh_access_token(username):
    tokens = user_tokens.get(username)
    if tokens:
        response = requests.post(f"{API_URL}/api/token/refresh/", data={'refresh': tokens['refresh_token']})
        if response.status_code == 200:
            new_tokens = response.json()
            access_token_decoded = jwt.decode(new_tokens['access'], JWT_SECRET, algorithms=[JWT_ALGORITHM])
            expiration_time = datetime.fromtimestamp(access_token_decoded['exp'])
            user_tokens[username]['access_token'] = new_tokens['access']
            user_tokens[username]['expires_at'] = expiration_time
            return new_tokens['access']
    return None


def get_access_token(username):
    tokens = user_tokens.get(username)
    if tokens:
        if datetime.now() >= tokens['expires_at'] - timedelta(seconds=30):  # Refresh if token is close to expiry
            new_access_token = refresh_access_token(username)
            if new_access_token:
                return new_access_token
        else:
            return tokens['access_token']
    return None


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
    embed_main.set_footer(text=f"Requested by: {finish_interaction.user.name}",
                          icon_url=finish_interaction.user.avatar.url)

    if embed2:
        await finish_interaction.followup.send(embeds=[embed_main, embed1, embed2], ephemeral=True)
    else:
        embed_main.set_image(url=chosen_card.get('image_uris').get('normal'))
        await finish_interaction.followup.send(embed=embed_main, ephemeral=True)


# Command: /authenticate
@bot.tree.command(name='authenticate', description='Authenticate with the bot')
async def authenticate(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"[Click here to authenticate]({OAUTH_URL})", ephemeral=True)


# Command: /get_card <name>
@bot.tree.command(name='get_card', description='Get information about a Magic: The Gathering card')
async def card(interaction: discord.Interaction, name: str):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    valid_users = await get_valid_users(guild)
    response = requests.get(f"{API_URL}/api/get_card/", json= {'name': name,
                                                           'type': 'card',
                                                           'valid_users': valid_users})
    if response.status_code == 200:
        card_data = response.json()
        user_list = card_data.get('users', [])
        finish = card_data.get('finishes', [])[0]
        await create_embed(interaction, card_data, finish, user_list)
    else:
        logger.error(f'Failed to retrieve card: {response.status_code}')
        await interaction.followup.send('Failed to retrieve card.')


# Command: /get_printing <name>
@bot.tree.command(name='get_printing', description='Get a specific printing of a Magic: The Gathering card')
async def card(card_interaction: discord.Interaction, name: str):
    await card_interaction.response.defer(ephemeral=True)
    guild = card_interaction.guild
    valid_users = await get_valid_users(guild)
    response = requests.get(f"{API_URL}/api/get_card/", json={'name': name,
                                                              'type': 'printing',
                                                              'valid_users': valid_users})
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
                await set_interaction.response.defer(ephemeral=True)
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
                                await finish_interaction.response.defer(ephemeral=True)
                                selected_finish = None
                                chosen_finish = finish_interaction.data.get('values')[0]
                                for each_finish in selected_card.get('finishes'):
                                    if f"{each_finish}" == chosen_finish:
                                        selected_finish = each_finish
                                        break
                                if selected_finish:
                                    await create_embed(finish_interaction, selected_card, selected_finish, users)
                                else:
                                    logger.error(f"Failed to select finish: {chosen_finish}")
                                    await finish_interaction.followup.send("Failed to select finish.")

                            finish_select.callback = select_finish
                            finish_view = discord.ui.View()
                            finish_view.add_item(finish_select)
                            await set_interaction.followup.send("Choose a finish:",
                                                                        view=finish_view,
                                                                        ephemeral=True)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.followup.send("Choose a printing:", view=view, ephemeral=True)

        await display_options(card_interaction, 0)

    else:
        logger.error(f'Failed to retrieve card: {response.status_code}')
        await card_interaction.followup.send('Failed to retrieve card.')


# Command: /create_user <password>
@bot.tree.command(name='create_user', description='Create a new user')
async def create_user(interaction: discord.Interaction, password: str):
    await interaction.response.defer(ephemeral=True)
    user_id = interaction.user.id
    username = interaction.user.name
    user_password = password
    data = {
        'discord_id': user_id,
        'username': username,
        'password': user_password
    }
    response = requests.post(f"{API_URL}/api/create_user/", json=data)
    if response.status_code == 201:
        await interaction.followup.send('User created successfully!')
    elif response.status_code == 400:
        await interaction.followup.send(response.json()['error'])


# Command: /show_users
@bot.tree.command(name='show_users', description='Show all users in discord server')
async def show_users(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    valid_users = await get_valid_users(guild)
    response = requests.get(f"{API_URL}/api/get_users/", json={"valid_users": valid_users})
    if response.status_code == 200:
        user_list = response.json()
        output = "Users:\n"
        for user in user_list:
            output += f"**{user['username']}**\n"
        await interaction.followup.send(output)
    else:
        await interaction.followup.send('Failed to retrieve users.')


# Command: /delete_user
@bot.tree.command(name='delete_user', description='Delete a user')
async def delete_user(interaction: discord.Interaction, password: str):
    await interaction.response.defer(ephemeral=True)
    data = {
        'username': interaction.user.name,
        'password':  password,
    }
    response = requests.post(f"{API_URL}/api/delete_user/", json=data)
    if response.status_code == 200:
        await interaction.followup.send('User deleted successfully!')
    else:
        await interaction.followup.send('Failed to delete user.')


# Command: /create_collection
@bot.tree.command(name='create_collection', description='Create a new collection')
async def create_collection(interaction: discord.Interaction, collection_name: str):
    await interaction.response.defer(ephemeral=True)
    username = interaction.user.name

    # Fetch tokens for the user if not already fetched
    if username not in user_tokens:
        tokens = fetch_tokens(username)
        if tokens is None:
            await interaction.followup.send('You need to authenticate first. Use /authenticate command.',
                                            ephemeral=True)
            return

    # Get a valid access token
    access_token = get_access_token(username)
    if access_token is None:
        await interaction.followup.send('Authentication failed. Please re-authenticate using /authenticate command.',
                                        ephemeral=True)
        return

    headers = {
        'Authorization': f'Bearer {tokens["access_token"]}'
    }
    data = {
        'username': username,
        'collection_name': collection_name
    }
    response = requests.post(f"{API_URL}/api/create_collection/", json=data, headers=headers)
    if response.status_code == 201:
        await interaction.followup.send('Collection created successfully!')
    else:
        await interaction.followup.send('Failed to create collection.')


# Command: /get_collection
@bot.tree.command(name='get_collection', description='Get your collection')
async def get_collection(interaction: discord.Interaction, collection_name: str):
    await interaction.response.defer(ephemeral=True)
    username = interaction.user.name
    data = {
        'username': username,
        'collection_name': collection_name
    }
    response = requests.get(f"{API_URL}/api/get_collection/", json=data)
    if response.status_code == 200:
        collection = response.json()
        if collection:
            card_count = collection[0]['card_count']
            total_value = collection[0]['total_value']
            embed = discord.Embed(title=f"{interaction.user.name}'s {collection_name} Collection")
            embed.add_field(name="Card Count", value=card_count, inline=True)
            embed.add_field(name="Total Value", value=f"${total_value}", inline=True)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send('No card_manager found in your collection.')
    else:
        await interaction.followup.send('Failed to retrieve collection.')


# Command: /show_collections
@bot.tree.command(name='show_collections', description='Show all collections for a user')
async def show_collections(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    username = interaction.user.name
    data = {
        'username': username
    }
    response = requests.get(f"{API_URL}/api/get_collections/", json=data)
    if response.status_code == 200:
        collections = response.json()
        output = "Collections:\n"
        for collection in collections:
            output += f"**{collection['collection_name']}**\n"
        await interaction.followup.send(output)
    else:
        await interaction.followup.send('Failed to retrieve collections.')


# Command: /add_to_collection
@bot.tree.command(name='add_to_collection', description='Add a card to your collection')
async def add(interaction: discord.Interaction, collection_name: str):
    await interaction.response.send_message("Please reply to this message with your CSV file attached.")
    message = await interaction.original_response()
    prompt_message_ids[interaction.user.id] = {
        'message_id': message.id,
        'collection_name': collection_name,
        'action': 'add',
        'interaction': interaction
    }


# Command: /update_collection
@bot.tree.command(name="update_collection", description="Upload a CSV file to update your collection")
async def upload(interaction: discord.Interaction, collection_name: str):
    await interaction.response.send_message("Please reply to this message with your CSV file attached.")
    message = await interaction.original_response()
    prompt_message_ids[interaction.user.id] = {
        'message_id': message.id,
        'collection_name': collection_name,
        'action': 'update',
        'interaction': interaction
    }


# Event listener for when a message is sent
@bot.event
async def on_message(message):
    # Check if the message is from the user who uploaded the CSV file
    user_id = message.author.id
    if user_id in prompt_message_ids:
        if message.attachments:
            if message.reference and message.reference.message_id:
                if message.reference.message_id == prompt_message_ids[user_id]['message_id']:
                    interaction = prompt_message_ids[user_id]['interaction']
                    await interaction.followup.send("Uploading your CSV file...", ephemeral=True)
                    prompt_message = await message.channel.fetch_message(prompt_message_ids[user_id]['message_id'])
                    await prompt_message.delete()
                    for attachment in message.attachments:
                        if attachment.filename.endswith('.csv'):
                            async with aiohttp.ClientSession() as session:
                                async with session.get(attachment.url) as response:
                                    if response.status == 200:
                                        data = await response.read()
                                        form = aiohttp.FormData()
                                        form.add_field('file', data,
                                                       filename=attachment.filename, content_type='text/csv')
                                        form.add_field('action', prompt_message_ids[user_id]['action'])
                                        form.add_field('username', message.author.name)
                                        form.add_field('collection_name',
                                                       prompt_message_ids[user_id]['collection_name'])
                                        await message.delete()
                                        async with session.post(f'{API_URL}/api/update_collection/',
                                                                data=form) as api_response:
                                            if api_response.status == 200:
                                                await interaction.followup.send(
                                                    content="Collection updated successfully!", ephemeral=True
                                                )

                                            else:
                                                await interaction.followup.send(
                                                    content="Failed to update collection.", ephemeral=True
                                                )

                            del prompt_message_ids[user_id]


# Command: Delete a user's collection
@bot.tree.command(name='delete_collection', description='Delete a collection')
async def delete_collection(interaction: discord.Interaction, collection_name: str):
    await interaction.response.defer(ephemeral=True)
    username = interaction.user.name
    data = {
        'username': username,
        'collection_name': collection_name
    }
    response = requests.post(f"{API_URL}/api/delete_collection/", json=data)
    if response.status_code == 200:
        await interaction.followup.send('Collection deleted successfully!')
    else:
        await interaction.followup.send('Failed to delete collection.')


# Command: /hello
@bot.tree.command(name='hello', description='Say hello!')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')


# Run the bot
def run_bot():
    bot.run(BOT_TOKEN)
