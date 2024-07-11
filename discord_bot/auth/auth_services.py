import jwt
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_URL = os.getenv('API_URL')
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('card_manager')


class AuthServices:
    def __init__(self):
        self.user_tokens = {}

    def save_tokens(self, username, tokens):
        access_token_decoded = jwt.decode(tokens['access'], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        expiration_time = datetime.fromtimestamp(access_token_decoded['exp'])
        self.user_tokens[username] = {
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh'],
            'expiration_time': expiration_time
        }

    def fetch_tokens(self, username):
        logger.info(f'Sent JWT_SECRET: {JWT_SECRET}')
        response = requests.get(f"{API_URL}/api/fetch_tokens/",
                                json={'username': username, 'jwt_secret': JWT_SECRET})
        if response.status_code == 200:
            tokens = response.json()
            logger.info(f'Fetched tokens for user {username}, Tokens: {tokens}')
            self.save_tokens(username, tokens)
            return tokens
        return None

    async def handle_oauth_callback(self, ctx, code):
        logger.info(f'Got here lmao wtf')
        response = requests.get(f"{API_URL}/api/oauth_callback/", params={'code': code})
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(ctx.author.name, tokens)
            await ctx.send(f'Authenticated successfully for user {ctx.author.name}')
        else:
            await ctx.send('Authentication failed')

    def refresh_access_token(self, username):
        tokens = self.user_tokens.get(username)
        if tokens:
            response = requests.post(f"{API_URL}/api/token/refresh/", json={'refresh': tokens['refresh']})
            if response.status_code == 200:
                new_tokens = response.json()
                self.save_tokens(username, new_tokens)
                return new_tokens['access']
        return None

    def get_access_token(self, username):
        tokens = self.user_tokens.get(username)
        if tokens:
            if datetime.now() >= tokens['expiration_time'] - timedelta(seconds=30):
                return self.refresh_access_token(username)
            else:
                return tokens['access_token']
        return None

    def get_user_tokens(self):
        return self.user_tokens

    def set_user_tokens(self, user_tokens):
        self.user_tokens = user_tokens
