from ..repositories.user_repository import UserRepository
from ..repositories.collection_repository import CollectionRepository


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.collection_repository = CollectionRepository()

    # Create a new user with a collection
    def create_user_with_collection(self, validated_data):
        user = self.user_repository.create_user(validated_data)
        collection = self.collection_repository.create_collection(user)
        user.collection = collection
        user.save()
        return user

    def get_all_users(self):
        return self.user_repository.get_all_users()

    def change_username(self, discord_id, new_username):
        return self.user_repository.change_username(discord_id, new_username)

    def delete_user(self, discord_id):
        return self.user_repository.delete_user(discord_id)
