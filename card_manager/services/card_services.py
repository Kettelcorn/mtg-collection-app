from ..repositories.card_repository import CardRepository
from ..repositories.user_repository import UserRepository
import requests
import json
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CardService:
    def __init__(self):
        self.card_repository = CardRepository()
        self.user_repository = UserRepository()

    # Get card details from scrfall API, and return information about the card and users who own the card
    def fetch_card_details(self, card_name, search_type, scryfall_url):
        params = {
            'fuzzy': card_name
        }
        response = requests.get(scryfall_url, params=params)
        if response.status_code != 200:
            return None, response.status_code
        card_details = response.json()
        card_name = card_details.get('name')
        users = {}
        for user in self.user_repository.get_all_users():
            collection = user.collection
            cards = self.card_repository.get_cards_by_collection_and_name(collection, card_name)
            logger.info(f"Found {len(cards)} cards for {user.discord_username}")
            if cards:
                for card in cards:
                    if user.discord_username not in users:
                        users[user.discord_username] = []
                    users[user.discord_username].append({
                        "username": user.discord_username,
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
