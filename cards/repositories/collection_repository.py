from ..models import Collection


class CollectionRepository:
    # Create a collection
    @staticmethod
    def create_collection(user):
        return Collection.objects.create(user=user)

    # Get collection by user id
    @staticmethod
    def get_collection_by_user_id(user_id):
        return Collection.objects.get(user=user_id)
