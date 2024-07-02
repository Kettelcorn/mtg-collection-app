from ..models import Card
import logging

logger = logging.getLogger(__name__)

class CardRepository:
    # Create a card
    def create_card(self, card_data, collection):
        return Card.objects.create(**card_data, collection=collection)

    def create_cards(self, all_cards, collection):
        try:
            for card_data in all_cards:
                card_data['collection'] = collection
            objects_to_create = [Card(**card_data) for card_data in all_cards]
            logger.info(f"Creating {len(objects_to_create)} cards")
            return Card.objects.bulk_create(objects_to_create)
        except Exception as e:
            logger.error(f"Error creating cards: {e}")
            return None

    # Get card by collection and name
    def get_cards_by_collection_and_name(self, collection, card_name):
        return collection.cards.filter(card_name=card_name)

    # Get card by tcg_id and finish
    def get_card_by_tcg_id_and_finish(self, tcg_id, finish):
        return Card.objects.get(tcg_id=tcg_id, finish=finish)

    # Update the price of a card
    def update_card_price(self, card, price):
        card.price = price
        card.save()

    def delete_card(self, card):
        card.delete()
        return card
