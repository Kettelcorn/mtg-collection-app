from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
import os
from dotenv import load_dotenv
from .services.card_services import CardService
from .services.collection_services import CollectionService
from .services.user_services import UserService
from .serializers import UserSerializer
from decimal import Decimal

logger = logging.getLogger(__name__)
load_dotenv()
# TODO: Remove scryfall urls from env file and other non-sensitive data
SCRYFALL_URL = os.getenv('SCRYFALL_URL')


# Get card data from Scryfall API
class GetCardView(APIView):
    def get(self, request, *args, **kwargs):
        card_name = request.query_params.get('name')
        search_type = request.query_params.get('type')
        if card_name:
            try:
                card_service = CardService()
                card_details, status_code = card_service.fetch_card_details(card_name, search_type, SCRYFALL_URL)
                if status_code == 200:
                    return Response(card_details, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Card not found'}, status=status_code)
            except Exception as e:
                logger.error(f"Error fetching card details: {e}")
                return Response({"detail": "An error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No card name provided'}, status=400)


# Get collection data for a user
class GetCollectionView(APIView):
    def get(self, request, *args, **kwargs):
        discord_id = request.query_params.get('discord_id')
        if discord_id:
            try:
                user_service = UserService()
                user = user_service.user_repository.get_user_by_discord_id(discord_id)
                collection_service = CollectionService()
                card_list = collection_service.get_collection_details(user)
                return Response(card_list, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error fetching collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id provided'}, status=400)


# Update collection data for a user
class UpdateCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        action = request.data.get('action')
        discord_id = request.data.get('discord_id')

        if csv_file and action and discord_id:
            try:
                user_service = UserService()
                user = user_service.user_repository.get_user_by_discord_id(discord_id)
                collection_service = CollectionService()
                response_data, status_code = collection_service.process_csv_and_update_collection(
                    csv_file,
                    user
                )
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No file, action, or discord_id provided'}, status=400)


# Create a new user
class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUsersView(APIView):
    def get(self, request, *args, **kwargs):
        user_service = UserService()
        users = user_service.get_all_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Ping endpoint to keep the application awake
class PingView(APIView):
    def post(self, request, *args, **kwargs):
        response_data = {'message': 'Data received successfully'}
        return Response(response_data, status=status.HTTP_200_OK)
