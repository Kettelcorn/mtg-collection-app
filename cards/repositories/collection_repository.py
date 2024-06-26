from ..models import Collection


class CollectionRepository:
    def create_collection(self, user):
        return Collection.objects.create(user=user)

    def get_collection_by_user_id(self, user_id):
        return Collection.objects.get(user=user_id)