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
        try:
            url = "https://api.scryfall.com/cards/collection"
            headers = {"Content-Type": "application/json"}
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            card_list = [row for row in reader]
            logger.info(f"{len(card_list)} cards found")
            identifiers = []
            scryfall_data = []
            value_map = {}
            count = 0
            total_quantity = 0
            total_sent = 0

            for card in card_list:
                backup_url = "https://api.scryfall.com/cards/"
                total_quantity += int(card['Quantity'])
                collector_number = card.get('Card Number') or card.get('Collector number')
                set_code = card.get('Set Code') or card.get('Set code')
                if 'Product ID' in card:
                    backup_url += f"tcgplayer/{card['Product ID']}"
                elif 'Scryfall ID' in card:
                    backup_url += f"{card['Scryfall ID']}"

                value_map[f"{set_code}-{collector_number}"] = backup_url

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
                            logger.info(f"Card not found: {not_found}")
                            logger.info(f"Backup URL: {value_map[f'{not_found["set"]}-{not_found["collector_number"]}']}")
                            backup_response = requests.get(value_map[f"{not_found['set']}-{not_found['collector_number']}"])
                            if backup_response.status_code == 200:
                                logger.info(f"Backup response successful")
                                backup_data = backup_response.json()
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
            self.card_repository.delete_all_cards_by_collection(collection)

            index = 0
            for data in scryfall_data:
                for selected_card in data.get('data'):
                    name = selected_card.get('name')
                    if name == 'Mizzix of the Izmagnus':
                        logger.info(f"Mizzix found")
                        logger.info(f"Data: {selected_card}")
                    scryfall_id = selected_card.get('id')
                    tcgplayer_id = selected_card.get('tcgplayer_id') or 0
                    set_name = selected_card.get('set_name')
                    collector_number = selected_card.get('collector_number')
                    # TODO: Figure out way to keep track of finish for backup cards as the ordering gets messed up
                    #  with the current implementation (index doesn't match up with the original card list)
                    finish = None
                    if 'Foil' in card_list[index]:
                        if card_list[index]['Foil'] == 'normal':
                            finish = 'nonfoil'
                        elif card_list[index]['Foil'] == 'foil':
                            finish = 'foil'
                        elif card_list[index]['Foil'] == 'etched':
                            finish = 'etched'
                    elif 'Printing' in card_list[index]:
                        if card_list[index]['Printing'] == 'Normal':
                            finish = 'nonfoil'
                        elif card_list[index]['Printing'] == 'Foil':
                            for finish_option in selected_card.get('finishes'):
                                if finish_option == 'etched':
                                    finish = 'etched'
                                elif finish_option == 'foil':
                                    finish = 'foil'
                                    break

                    if finish is None:
                        finish = 'none'
                    uri = selected_card.get('uri')
                    price = None
                    if finish == 'foil':
                        price = selected_card.get('prices').get('usd_foil')
                    elif finish == 'nonfoil':
                        price = selected_card.get('prices').get('usd')
                    elif finish == 'etched':
                        price = selected_card.get('prices').get('usd_etched')
                    if price is None:
                        price = Decimal(0.00)
                    quantity = card_list[index]['Quantity']

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
                    index += 1

            return {'message': 'Data received successfully'}, status.HTTP_200_OK

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {'error': 'An error occurred'}, status.HTTP_500_INTERNAL_SERVER_ERROR
