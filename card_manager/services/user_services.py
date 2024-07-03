from ..repositories.user_repository import UserRepository
from ..repositories.collection_repository import CollectionRepository
from django.contrib.auth import authenticate


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.collection_repository = CollectionRepository()

    # Create a new user with a collection (discord id is optional)
    def create_user(self, username, password, discord_id):
        user = self.user_repository.create_user(username, password, discord_id)
        return user

    # Authenticate a user
    def authenticate_user(self, username, password):
        return authenticate(username=username, password=password)

    # Get all users
    def get_all_users(self):
        return self.user_repository.get_all_users()

    # Get a user by Discord ID
    def get_user_by_username(self, username):
        return self.user_repository.get_user_by_username(username)

    def get_user_by_discord_id(self, discord_id):
        return self.user_repository.get_user_by_discord_id(discord_id)

    # Change the username of a user
    def change_username(self, username, new_username):
        return self.user_repository.change_username(username, new_username)

    # Delete a user
    def delete_user(self, username):
        return self.user_repository.delete_user(username)
