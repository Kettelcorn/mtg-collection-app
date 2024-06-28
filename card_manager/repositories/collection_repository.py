from ..models import Collection


class CollectionRepository:
    # Create a collection
    def create_collection(self, user):
        return Collection.objects.create(user=user)

    # Get collection by user id
    def get_collection_by_user_id(self, user_id):
        return Collection.objects.get(user=user_id)

    # Remove all card_manager from a collection
    def clear_collection(self, user_id):
        collection = Collection.objects.get(user=user_id)
        collection.cards.all().delete()
        return collection
