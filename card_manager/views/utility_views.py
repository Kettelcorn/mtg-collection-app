from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.generic.base import RedirectView
from django.shortcuts import redirect
import logging
import os
from dotenv import load_dotenv
from ..services.utility_services import UtilityServices
from ..services.user_services import UserService
import jwt
from datetime import datetime, timedelta

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
API_URL = os.getenv('API_URL')
OAUTH_URL = os.getenv('OAUTH_URL')
JWT_SECRET = os.getenv('JWT_SECRET')


logger = logging.getLogger('card_manager')


# Ping endpoint to keep the application awake
class PingView(APIView):
    def post(self, request, *args, **kwargs):
        response_data = {'message': 'Data received successfully'}
        return Response(response_data, status=status.HTTP_200_OK)


class OAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        utility_services = UtilityServices()
        try:
            logger.info(f"OAuth callback: {request.query_params}")
            user_info = utility_services.oauth_callback(request)
            user = user_info.get('user')
            refresh = RefreshToken.for_user(user)
            utility_services.save_tokens(user, str(refresh.access_token), str(refresh))
            return redirect(f"https://discord.com/channels/@me?access={refresh.access_token}&refresh={refresh}")
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StartOAuthView(RedirectView):
    def get(self, request, *args, **kwargs):
        return redirect(OAUTH_URL)


class FetchTokensView(APIView):
    def get(self, request, *args, **kwargs):
        jwt_secret = request.data.get('jwt_secret')
        if jwt_secret != JWT_SECRET:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        username = request.data.get('username')
        try:
            user_service = UserService()
            user = user_service.get_user_by_username(username)
            refresh = RefreshToken.for_user(user)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            logger.info(f"Tokens fetched for {username}")
            return Response(tokens, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching tokens: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh = request.data.get('refresh_token')
            refresh = RefreshToken(refresh)
            return Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_400_BAD_REQUEST)
