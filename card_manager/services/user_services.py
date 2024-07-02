from ..repositories.user_repository import UserRepository
from ..repositories.collection_repository import CollectionRepository


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.collection_repository = CollectionRepository()

    # Create a new user with a collection
    def create_user(self, discord_id, discord_username):
        user = self.user_repository.create_user(discord_id, discord_username)
        user.save()
        return user

    # Get all users
    def get_all_users(self):
        return self.user_repository.get_all_users()

    # Get a user by Discord ID
    def get_user_by_discord_id(self, discord_id):
        return self.user_repository.get_user_by_discord_id(discord_id)

    # Change the username of a user
    def change_username(self, discord_id, new_username):
        return self.user_repository.change_username(discord_id, new_username)

    # Delete a user
    def delete_user(self, discord_id):
        return self.user_repository.delete_user(discord_id)
