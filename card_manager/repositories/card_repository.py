from ..models import Card


class CardRepository:
    # Get card by collection and name
    def get_cards_by_collection_and_name(self, collection, card_name):
        return collection.cards.filter(card_name=card_name)

    # Get card by tcg_id and finish
    def get_card_by_tcg_id_and_finish(self, tcg_id, finish):
        return Card.objects.get(tcg_id=tcg_id, finish=finish)

    # Delete all cards by collection
    def delete_all_cards_by_collection(self, collection):
        collection.cards.all().delete()

    # Create a card
    def create_card(self, card_data):
        return Card.objects.create(**card_data)

    # Update the price of a card
    def update_card_price(self, card, price):
        card.price = price
        card.save()
