from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..services.user_services import UserService
from ..serializers import UserSerializer
from django.contrib.auth import authenticate

logger = logging.getLogger('card_manager')


# Create a new user
class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        discord_id = request.data.get('discord_id')
        if username and password:
            user_service = UserService()
            if user_service.get_user_by_username(username):
                logger.error(f"/api/create_user/: User already exists {status.HTTP_400_BAD_REQUEST}")
                return Response({'error': 'User already exists'}, status=400)
            user = user_service.create_user(username, password, discord_id)
            serializer = UserSerializer(user)
            logger.info(f"/api/create_user/: User created: {username} {status.HTTP_201_CREATED}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"/api/create_user/: No username or password provided {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'No discord_id or discord_username provided'}, status=400)


class GetUsersView(APIView):
    def get(self, request, *args, **kwargs):
        valid_users = request.data.get('valid_users', [])
        user_service = UserService()
        users = user_service.get_all_users(valid_users)
        serializer = UserSerializer(users, many=True)
        logger.info(f"/api/get_users/: All users retrieved: {users} {status.HTTP_200_OK}")
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        new_username = request.data.get('new_username')
        if username and new_username:
            user_service = UserService()
            user = user_service.change_username(username, new_username)
            serializer = UserSerializer(user)
            logger.info(f"/api/change_username/: Username changed: {username} -> {new_username} {status.HTTP_200_OK}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.error(f"/api/change_username/: No username or new_username provided {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'No username or new_username provided'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            user_service = UserService()
            user_service.delete_user(username)
            logger.info(f"/api/delete_user/: User deleted: {username} {status.HTTP_200_OK}")
            return Response({'message': 'User deleted'}, status=status.HTTP_200_OK)
        else:
            logger.error(f"/api/delete_user/: User not found: {username} {status.HTTP_404_NOT_FOUND}")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
