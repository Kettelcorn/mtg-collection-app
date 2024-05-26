import requests
import json
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
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logging.error(f'Failed to parse JSON: {e}')
            return None
    else:
        logging.error(f'Failed to download bulk data: {response.status_code}')
        return None


def process_bulk_data(json_data):
    if not json_data:
        logging.error('No data to process')
        return

    cards = json_data
    logging.info(f'Processing {len(cards)} cards')
    count = 0
    new_cards = []

    existing_cards = set(Card.objects.values_list('name', flat=True))

    for card in cards:
        count += 1
        logging.info(f'Processing card: {count}')
        card_data = {
            'description': card.get('oracle_text', ''),
            'power': card.get('power', ''),
            'toughness': card.get('toughness', ''),
            'colors': ', '.join(card.get('colors', [])),
            'rarity': card.get('rarity', ''),
            'set_name': card.get('set_name', ''),
            'image_url': card.get('image_uris', {}).get('normal', ''),
            'price': card['prices'].get('usd', 0.0) if card['prices'].get('usd') else 0.0
        }

        if card['name'] in existing_cards:
            Card.objects.filter(name=card['name']).update(**card_data)
        else:
            new_cards.append(Card(name=card['name'], **card_data))

    if new_cards:
        Card.objects.bulk_create(new_cards)
        logging.info(f'Created {len(new_cards)} new cards')

    logging.info('Finished processing cards')
