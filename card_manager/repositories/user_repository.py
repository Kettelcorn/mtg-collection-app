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
        else:
            return None

    def create_discord_user(self, discord_id, discord_username, discord_discriminator, discord_email):
        user, created = User.objects.update_or_create(
            discord_id=discord_id,
            defaults={
                'username': discord_username,
                'discord_username': discord_username,
                'discord_discriminator': discord_discriminator,
                'email': discord_email,
                'discord_email': discord_email
            }
        )
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
    def get_all_users(self, valid_users):
        try:
            return User.objects.filter(username__in=valid_users)
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

    def save_tokens(self, user, access_token, refresh_token):
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.save()
        return user
