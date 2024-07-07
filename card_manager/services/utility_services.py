import requests
import os
from dotenv import load_dotenv
import logging
from django.contrib.auth import login
from ..repositories.user_repository import UserRepository

logger = logging.getLogger('django')

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
API_URL = os.getenv('API_URL')
OAUTH_URL = os.getenv('OAUTH_URL')


class UtilityServices:
    def oauth_callback(self, request):
        code = request.query_params.get('code')
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f'{API_URL}/api/oauth_callback/'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        logger.info(f"{data} {headers}")
        try:
            response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            access_token = response_data.get('access_token')

            if access_token:
                user_info_response = requests.get(
                    'https://discord.com/api/users/@me',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info = user_info_response.json()

                discord_id = user_info.get('id')
                username = user_info.get('username')
                discriminator = user_info.get('discriminator')
                email = user_info.get('email')

                user_repository = UserRepository()
                user = user_repository.create_discord_user(discord_id, username, discriminator, email)

                login(request, user)

                return {
                    'message': 'User authenticated',
                    'user': user,
                    'user_info': user_info
                        }
            else:
                return {'error': 'Failed to obtain access token'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user info: {e}")
            return {'error': 'An error occurred'}

    def save_tokens(self, user, access_token, refresh_token):
        user_repository = UserRepository()
        user_repository.save_tokens(user, access_token, refresh_token)
