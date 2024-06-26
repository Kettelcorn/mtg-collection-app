from ..models import Card


class CardRepository:
    # Get card by collection and name
    def get_cards_by_collection_and_name(self, collection, card_name):
        return collection.cards.filter(card_name=card_name)

    # Delete all cards by collection
    def delete_all_cards_by_collection(self, collection):
        collection.cards.all().delete()

    # Create a card
    def create_card(self, card_data):
        return Card.objects.create(**card_data)
