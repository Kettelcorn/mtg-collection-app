from ..repositories.collection_repository import CollectionRepository
from ..repositories.card_repository import CardRepository
from ..repositories.user_repository import UserRepository
from decimal import Decimal
import requests
import json
import time
import csv
import logging
from rest_framework import status

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self):
        self.collection_repository = CollectionRepository()
        self.card_repository = CardRepository()
        self.user_repository = UserRepository()

    # Get collection details for a user
    def get_collection_details(self, user):
        collection = self.collection_repository.get_collection_by_user_id(user)
        cards = collection.cards.all()
        card_list = []
        total_value = Decimal(0.00)
        total_quantity = 0
        for card in cards:
            card_list.append({
                'card_name': card.card_name,
                'scryfall_id': card.scryfall_id,
                'tcg_id': card.tcg_id,
                'set': card.set,
                'collector_number': card.collector_number,
                'finish': card.finish,
                'print_uri': card.print_uri,
                'price': card.price,
                'quantity': card.quantity
            })
            total_value += card.price * card.quantity
            total_quantity += card.quantity
        card_list.insert(0, {"card_count": total_quantity, "total_value": total_value})
        return card_list

    # Process CSV file and update collection#
    def process_csv_and_update_collection(self, csv_file, user):
        # TODO: Split into two smaller functions
        # Parse CSV and get card info from scryfall (part 1)
        try:
            url = "https://api.scryfall.com/cards/collection"
            headers = {"Content-Type": "application/json"}
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            card_list = [row for row in reader]
            logger.info(f"{len(card_list)} unique cards found")
            identifiers, scryfall_data = [], []
            finish_map = {}
            count, total_quantity, total_sent = 0, 0, 0

            for card in card_list:
                backup_url = "https://api.scryfall.com/cards/"
                total_quantity += int(card['Quantity'])
                collector_number = card.get('Card Number') or card.get('Collector number')
                set_code = card.get('Set Code') or card.get('Set code')

                if 'Product ID' in card:
                    backup_url += f"tcgplayer/{card['Product ID']}"
                elif 'Scryfall ID' in card:
                    backup_url += f"{card['Scryfall ID']}"

                finish = None
                if 'Foil' in card:
                    finish = card['Foil'].lower()
                elif 'Printing' in card:
                    finish = card['Printing'].lower()
                if finish == 'normal':
                    finish = 'nonfoil'

                finish_map[f"{set_code}-{collector_number}".upper()] = {
                    'backup_url': backup_url,
                    'finish': finish,
                    'quantity': card['Quantity']
                }

                identifiers.append({
                    'collector_number': collector_number,
                    'set': set_code
                })
                count += 1
                if len(identifiers) == 75 or count == len(card_list):
                    logger.info(f"Identifiers length: {len(identifiers)}")
                    total_sent += len(identifiers)
                    body = {"identifiers": identifiers}
                    response = requests.post(url, headers=headers, data=json.dumps(body))
                    if response.status_code == 200:
                        data = response.json()
                        for not_found in data.get('not_found'):
                            card_key = f'{not_found["set"]}-{not_found["collector_number"]}'.upper()
                            logger.info(f"Card not found: {card_key}")
                            logger.info(f"Backup URL: {finish_map[card_key]['backup_url']}")
                            backup_url = finish_map[card_key]['backup_url']
                            logger.info(f"Backup URL: {backup_url}")
                            backup_response = requests.get(backup_url)
                            if backup_response.status_code == 200:
                                logger.info(f"Backup response successful")
                                backup_data = backup_response.json()
                                new_key = f"{backup_data.get('set')}-{backup_data.get('collector_number')}".upper()
                                finish_map[new_key] = {
                                    'finish': finish_map[card_key]['finish'],
                                    'quantity': finish_map[card_key]['quantity']
                                }
                                data['data'].append(backup_data)
                            else:
                                logger.error(f"Error fetching card details: {backup_response.json()}")
                        scryfall_data.append(data)
                    else:
                        logger.error(f"Error fetching card details: {response.json()}")
                    identifiers = []

            logger.info(f"Total quantity in csv: {total_quantity}")
            logger.info(f"Total sent to Scryfall: {total_sent}")

            collection = user.collection

            # TODO: Only have this line of code in updating collection
            self.card_repository.delete_all_cards_by_collection(collection)

            # Add cards to collection (part 2)
            error_count = 0
            for data in scryfall_data:
                for selected_card in data.get('data'):
                    name = selected_card.get('name')
                    scryfall_id = selected_card.get('id')
                    tcgplayer_id = selected_card.get('tcgplayer_id') or 0
                    set_name = selected_card.get('set_name')
                    collector_number = selected_card.get('collector_number')
                    uri = selected_card.get('uri')

                    key = f'{selected_card.get('set')}-{collector_number}'.upper()
                    finish = finish_map[key]['finish']
                    quantity = finish_map[key]['quantity']

                    found_finish = None
                    for finish_option in selected_card.get('finishes'):
                        if finish_option == finish:
                            found_finish = finish
                            break
                        elif finish_option == 'etched' and finish == 'foil':
                            found_finish = 'etched'
                            break
                    if found_finish is None:
                        logger.error(f"Finish not found for {name} - {set_name} - {collector_number}")
                        error_count += 1
                        continue

                    price = None
                    if finish == 'nonfoil':
                        price = selected_card.get('prices').get('usd')
                    elif finish == 'foil':
                        price = selected_card.get('prices').get('usd_foil')
                    elif finish == 'etched':
                        price = selected_card.get('prices').get('usd_etched')

                    if price is None:
                        price = Decimal(0.00)

                    card_data = {
                        'card_name': name,
                        'scryfall_id': scryfall_id,
                        'tcg_id': tcgplayer_id,
                        'set': set_name,
                        'collector_number': collector_number,
                        'finish': finish,
                        'print_uri': uri,
                        'collection': collection,
                        'price': price,
                        'quantity': quantity
                    }
                    self.card_repository.create_card(card_data)
            logger.info(f"Error count: {error_count}")
            return {'message': 'Data received successfully'}, status.HTTP_200_OK

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {'error': 'An error occurred'}, status.HTTP_500_INTERNAL_SERVER_ERROR
