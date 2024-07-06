from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic.base import RedirectView
from django.shortcuts import redirect
import logging
import os
from dotenv import load_dotenv
from ..services.utility_services import UtilityServices

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
API_URL = os.getenv('API_URL')
OAUTH_URL = os.getenv('OAUTH_URL')

logger = logging.getLogger('django')


# Ping endpoint to keep the application awake
class PingView(APIView):
    def post(self, request, *args, **kwargs):
        response_data = {'message': 'Data received successfully'}
        return Response(response_data, status=status.HTTP_200_OK)


class OAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        utility_services = UtilityServices()
        try:
            user_info = utility_services.oauth_callback(request)
            return redirect('https://discord.com/channels/@me')
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StartOAuthView(RedirectView):
    def get(self, request, *args, **kwargs):
        oauth_url = (
            OAUTH_URL
        )
        return oauth_url
