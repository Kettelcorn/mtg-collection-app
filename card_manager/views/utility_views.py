from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
API_URL = os.getenv('API_URL')

logger = logging.getLogger('django')


# Ping endpoint to keep the application awake
class PingView(APIView):
    def post(self, request, *args, **kwargs):
        response_data = {'message': 'Data received successfully'}
        return Response(response_data, status=status.HTTP_200_OK)


class OAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        code = request.data.get('code')
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
        response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
        logger.debug(f"Discord token response status: {response.status_code}")
        logger.debug(f"Discord token response text: {response.text}")
        response_data = response.json()
        access_token = response_data.get('access_token')

        if access_token:
            # Use the access token to get user info
            user_info_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_info = user_info_response.json()
            logger.info(f"/api/oauth_callback/: User info retrieved: {user_info} {status.HTTP_200_OK}")
            return Response(user_info, status=status.HTTP_200_OK)
        else:
            logger.error(f"/api/oauth_callback/: Failed to obtain access token {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)
