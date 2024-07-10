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
        user_repository = UserRepository()
        response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
        if response.status_code == 200:
            oauth_data = response.json()
            user_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={'Authorization': f"Bearer {oauth_data.get('access_token')}"}
            )
            user_data = user_response.json()
            user = user_repository.get_user_by_username(user_data.get('username'))
            return {'user': user}
        else:
            return None

    def save_tokens(self, user, access_token, refresh_token):
        user_repository = UserRepository()
        user_repository.save_tokens(user, access_token, refresh_token)
