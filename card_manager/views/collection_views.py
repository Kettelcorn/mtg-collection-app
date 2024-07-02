from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..services.collection_services import CollectionService
from ..services.user_services import UserService

logger = logging.getLogger(__name__)


# Create a collection for a user
class CreateCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        discord_id = request.data.get('discord_id')
        collection_name = request.data.get('collection_name')
        if discord_id and collection_name:
            try:
                user_service = UserService()
                user = user_service.user_repository.get_user_by_discord_id(discord_id)
                collection_service = CollectionService()
                response_data, status_code = collection_service.create_collection(user, collection_name)
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error creating collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id or collection_name provided'}, status=400)


# Get collection data for a user
class GetCollectionsView(APIView):
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

        if csv_file and discord_id:
            try:
                user_service = UserService()
                user = user_service.user_repository.get_user_by_discord_id(discord_id)
                collection_service = CollectionService()
                scryfall_data, finish_map = collection_service.process_csv(csv_file)
                if action == 'update':
                    collection_service.clear_collection(user)
                response_data, status_code = collection_service.add_collection(user, scryfall_data, finish_map)
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No file, action, or discord_id provided'}, status=400)


# Delete collection data for a user
class DeleteCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        discord_id = request.data.get('discord_id')
        if discord_id:
            try:
                user_service = UserService()
                user = user_service.user_repository.get_user_by_discord_id(discord_id)
                collection_service = CollectionService()
                response_data, status_code = collection_service.clear_collection(user)
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error clearing collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id provided'}, status=400)

