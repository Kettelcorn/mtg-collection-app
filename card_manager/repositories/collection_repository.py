import logging

from ..models import Collection


class CollectionRepository:
    # Create a collection
    def create_collection(self, user, collection_name):
        return Collection.objects.create(user=user, collection_name=collection_name)

    # Get collection by user id
    def get_collection_by_name(self, user, collection_name):
        return Collection.objects.get(user=user, collection_name=collection_name)

    # Get all collection for a user
    def get_all_collections_by_user(self, user):
        return Collection.objects.filter(user=user)

    # Remove all card_manager from a collection
    def clear_collection(self, user, collection_name):
        collection = user.collections.get(collection_name=collection_name)
        collection.cards.all().delete()
        return collection

    def delete_collection(self, user, collection_name):
        collection = user.collections.get(collection_name=collection_name)
        collection.delete()
        logging.info(f"Deleted collection {collection_name}")
        return collection
