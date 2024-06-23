from ..models import Card

class CardRepository:
    def get_cards_by_collection_and_name(self, collection, card_name):
        return collection.cards.filter(card_name=card_name)

    def delete_all_cards_by_collection(self, collection):
        collection.cards.all().delete()

    def create_card(self, card_data):
        return Card.objects.create(**card_data)

    