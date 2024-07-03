from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..services.user_services import UserService
from ..serializers import UserSerializer
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


# Create a new user
class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        discord_id = request.data.get('discord_id')
        if username and password:
            user_service = UserService()
            logger.info(f'Creating user with username: {username}')
            if user_service.get_user_by_username(username):
                return Response({'error': 'User already exists'}, status=400)
            user = user_service.create_user(username, password, discord_id)
            logger.info(f'User created with username: {username}')
            serializer = UserSerializer(user)
            logger.info(f'Serializing user with username: {username}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'No discord_id or discord_username provided'}, status=400)


class GetUsersView(APIView):
    def get(self, request, *args, **kwargs):
        user_service = UserService()
        users = user_service.get_all_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        discord_id = request.data.get('discord_id')
        new_username = request.data.get('new_username')
        if discord_id and new_username:
            user_service = UserService()
            user = user_service.change_username(discord_id, new_username)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteUserView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        discord_id = request.data.get('discord_id')
        user = authenticate(username=username, password=password)
        if user:
            user_service = UserService()
            user_service.delete_user(username)
            return Response({'message': 'User deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
