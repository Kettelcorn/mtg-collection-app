from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..services.user_services import UserService
from ..serializers import UserSerializer
from decimal import Decimal


# Create a new user
class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        discord_id = request.data.get('discord_id')
        discord_username = request.data.get('discord_username')
        if discord_id and discord_username:
            user_service = UserService()
            if user_service.get_user_by_discord_id(discord_id):
                return Response({'error': 'User already exists'}, status=400)
            user = user_service.create_user(discord_id, discord_username)
            serializer = UserSerializer(user)
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
        discord_id = request.data.get('discord_id')
        if discord_id:
            user_service = UserService()
            user = user_service.delete_user(discord_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
