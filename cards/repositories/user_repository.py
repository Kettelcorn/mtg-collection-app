from ..models import User


class UserRepository:
    # Get user by discord id
    @staticmethod
    def get_user_by_discord_id(discord_id):
        return User.objects.get(discord_id=discord_id)

    # Create a user
    @staticmethod
    def create_user(validated_data):
        return User.objects.create(**validated_data)

    # Get all users
    @staticmethod
    def get_all_users():
        return User.objects.all()
