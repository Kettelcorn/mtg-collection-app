import requests
import json
from .models import Card
import logging
import time
from django.db import transaction



SCRYFALL_BULK_DATA_URL = 'https://api.scryfall.com/bulk-data'
CHUNK_SIZE = 1 * 1024 * 1024
DELAY_BETWEEN_REQUESTS = 5


def fetch_bulk_data_list():
    response = requests.get(SCRYFALL_BULK_DATA_URL)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Error fetching bulk data list')
        return None


def get_bulk_data_download_uri(data_type="default_cards"):
    bulk_data_list = fetch_bulk_data_list()
    if bulk_data_list:
        for bulk_data in bulk_data_list['data']:
            if bulk_data['type'] == data_type:
                return bulk_data['download_uri'], bulk_data['size']
    logging.error(f'No download URI found for data type: {data_type}')
    return None, None


def download_bulk_data(download_uri, total_size):
    start = 0
    data_bytes = bytearray()
    while start < total_size:
        end = min(start + CHUNK_SIZE - 1, total_size - 1)
        headers = {'Range': f'bytes={start}-{end}'}
        try:
            response = requests.get(download_uri, headers=headers)
            response.raise_for_status()
            data_bytes.extend(response.content)
            percent_complete = (end + 1) / total_size * 100
            logging.info(f'Downloaded {percent_complete:.2f}% of the bulk data')
        except requests.RequestException as e:
            logging.error(f'Failed to download bulk data: {e}')
            return
        start += CHUNK_SIZE
        time.sleep(DELAY_BETWEEN_REQUESTS)
    return bytes(data_bytes)


def process_bulk_data(data_bytes):
    try:
        data = data_bytes.decode('utf-8')
        json_data = json.loads(data)
        cards = json_data
        logging.info(f'Processing {len(cards)} cards')
        count = 0
        new_cards = []
        update_cards = []

        existing_cards = {card.name: card for card in Card.objects.all()}
        new_card_names = set()

        for card in cards:
            count += 1
            card_name = card['name']
            card_data = {
                'name': card_name,
                'description': card.get('oracle_text', ''),
                'power': card.get('power', ''),
                'toughness': card.get('toughness', ''),
                'colors': ', '.join(card.get('colors', [])),
                'rarity': card.get('rarity', ''),
                'set_name': card.get('set_name', ''),
                'image_url': card.get('image_uris', {}).get('normal', ''),
                'price': card['prices'].get('usd', 0.0) if card['prices'].get('usd') else 0.0
            }

            if card_name in existing_cards:
                existing_card = existing_cards[card_name]
                needs_update = False

                for key, value in card_data.items():
                    existing_value = getattr(existing_card, key)
                    if str(existing_value) != str(value):
                        setattr(existing_card, key, value)
                        needs_update = True
                if needs_update:
                    update_cards.append(existing_card)
                    logging.info(f'Updating card to list: {count}')
            elif card_name not in new_card_names:
                new_cards.append(Card(**card_data))
                new_card_names.add(card_name)
                logging.info(f'Adding card to list: {count}')
            else:
                logging.info(f'Skipping duplicate card: {count}')

        if update_cards:
            with transaction.atomic():
                for card in update_cards:
                    card.save(
                        update_fields=[
                            'description', 'power', 'toughness', 'colors', 'rarity', 'set_name', 'image_url', 'price'
                        ]
                    )
                logging.info(f'Updated {len(update_cards)} cards')

        if new_cards:
            logging.info(f'Checking {len(new_cards)} new cards')
            for card in new_cards:
                if card.name in existing_cards:
                    logging.warning(f'Card already exists: {card.name}')
                    new_cards.remove(card)
                else:
                    logging.warning(f'Card does not exist: {card.name}')
            Card.objects.bulk_create(new_cards)
            logging.info(f'Created {len(new_cards)} new cards')

        logging.info('Finished processing cards')
    except json.JSONDecodeError as e:
        logging.error(f'Failed to parse JSON: {e}')
    except Exception as e:
        logging.error(f'Error processing cards: {e}')