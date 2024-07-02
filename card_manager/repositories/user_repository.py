from ..models import User


class UserRepository:
    # Create a user
    def create_user(self, discord_id, discord_username):
        return User.objects.create(discord_id=discord_id, discord_username=discord_username)

    # Get user by discord id
    def get_user_by_discord_id(self, discord_id):
        try:
        # TODO: Change logic to be able to work with discord or user id
            return User.objects.get(discord_id=discord_id)
        except User.DoesNotExist:
            return None

    # Get all users
    def get_all_users(self):
        return User.objects.all()

    # Change the username of a user
    def change_username(self, discord_id, new_username):
        user = User.objects.get(discord_id=discord_id)
        user.discord_username = new_username
        user.save()
        return user

    # Delete a user
    def delete_user(self, discord_id):
        user = User.objects.get(discord_id=discord_id)
        user.delete()
        return user
