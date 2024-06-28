from ..models import User


class UserRepository:
    # Get user by discord id
    def get_user_by_discord_id(self, discord_id):
        return User.objects.get(discord_id=discord_id)

    # Create a user
    def create_user(self, validated_data):
        return User.objects.create(**validated_data)

    # Get all users
    def get_all_users(self):
        return User.objects.all()

    def change_username(self, discord_id, new_username):
        user = User.objects.get(discord_id=discord_id)
        user.discord_username = new_username
        user.save()
        return user

    def delete_user(self, discord_id):
        user = User.objects.get(discord_id=discord_id)
        user.delete()
        return user