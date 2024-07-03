from ..models import User


class UserRepository:
    # Create a user
    def create_user(self, username, password, discord_id):
        if username and password:
            if not discord_id:
                discord_id = 'None'
            user = User.objects.create_user(username=username, password=password, discord_id=discord_id)
            user.save()
            return user

    # Get user by discord id
    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user_by_discord_id(self, discord_id):
        try:
            return User.objects.get(discord_id=discord_id)
        except User.DoesNotExist:
            return None

    # Get all users
    def get_all_users(self):
        try:
            return User.objects.all()
        except User.DoesNotExist:
            return None

    # Change the username of a user
    def change_username(self, username, new_username):
        user = User.objects.get(username=username)
        user.username = new_username
        user.save()
        return user

    # Delete a user
    def delete_user(self, username):
        user = User.objects.get(username=username)
        user.delete()
        return user
