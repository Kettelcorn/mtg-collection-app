from ..models import Card


class CardRepository:
    # Get card by collection and name
    @staticmethod
    def get_cards_by_collection_and_name(collection, card_name):
        return collection.cards.filter(card_name=card_name)

    # Delete all cards by collection
    @staticmethod
    def delete_all_cards_by_collection(collection):
        collection.cards.all().delete()

    # Create a card
    @staticmethod
    def create_card(card_data):
        return Card.objects.create(**card_data)
