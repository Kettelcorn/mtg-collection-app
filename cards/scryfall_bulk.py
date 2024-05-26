import json
import requests
from .models import Card
import logging


SCRYFALL_BULK_DATA_URL = 'https://api.scryfall.com/bulk-data'


def fetch_bulk_data_list():
    response = requests.get(SCRYFALL_BULK_DATA_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_bulk_data_download_uri(data_type="default_cards"):
    bulk_data_list = fetch_bulk_data_list()
    if bulk_data_list:
        for bulk_data in bulk_data_list['data']:
            if bulk_data['type'] == data_type:
                return bulk_data['download_uri']
    return None


def download_bulk_data(download_uri):
    response = requests.get(download_uri)
    if response.status_code == 200:
        logging.info(f'Content-Type: {response.headers.get("Content-Type")}')
        logging.info(f'First 100 bytes of response: {response.content[:100]}')
        return response.content
    else:
        return None


def process_bulk_data(file_path):
    with open(file_path, 'r', encoding='UTF-8') as f:
        cards = json.load(f)
        for card in cards:
            Card.objects.update_or_create(
                name=card['name'],
                defaults={
                    'description': card.get('oracle_text', ''),
                    'power': card.get('power', ''),
                    'toughness': card.get('toughness', ''),
                    'colors': ', '.join(card.get('colors', [])),
                    'rarity': card.get('rarity', ''),
                    'set_name': card.get('set_name', ''),
                    'image_url': card.get('image_uris', {}).get('normal', ''),
                    'price': card['prices'].get('usd', 0.0) if card['prices'].get('usd') else 0.0
                }
            )