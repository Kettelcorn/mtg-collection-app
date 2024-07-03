from ..repositories.card_repository import CardRepository
from ..repositories.user_repository import UserRepository
from ..repositories.collection_repository import CollectionRepository
import requests
import json
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CardService:
    def __init__(self):
        self.card_repository = CardRepository()
        self.collection_repository = CollectionRepository()
        self.user_repository = UserRepository()

    # Get card details from scrfall API, and return information about the card and users who own the card
    def fetch_card_details(self, card_name, search_type, valid_users):
        params = {
            'fuzzy': card_name
        }
        response = requests.get('https://api.scryfall.com/cards/named', params=params)
        if response.status_code != 200:
            return None, response.status_code
        card_details = response.json()
        card_name = card_details.get('name')
        users = {}
        for user in self.user_repository.get_all_users(valid_users):
            collections = self.collection_repository.get_all_collections_by_user(user)
            for collection in collections:
                cards = self.card_repository.get_cards_by_collection_and_name(collection, card_name)
                logger.info(f"Found {len(cards)} cards for {user.username}")
                if cards:
                    for card in cards:
                        if user.username not in users:
                            users[user.username] = []
                        users[user.username].append({
                            "username": user.username,
                            "set": card.set,
                            "collector_number": card.collector_number,
                            "finish": card.finish,
                            "price": card.price,
                            "tcg_id": card.tcg_id,
                            "quantity": card.quantity
                        })
        card_details['users'] = users
        if search_type == 'printing':
            print_search_uri = card_details.get('prints_search_uri')
            if print_search_uri:
                print_response = requests.get(print_search_uri)
                if print_response.status_code == 200:
                    card_details['prints'] = print_response.json().get('data', [])
                    return card_details, 200
                else:
                    return None, print_response.status_code
        elif search_type == 'card':
            return card_details, 200
        else:
            return None, 400
