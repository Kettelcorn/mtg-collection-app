from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..services.collection_services import CollectionService
from ..services.user_services import UserService

logger = logging.getLogger(__name__)

# TODO: Figure out how to authenticate users when using this API


# Create a collection for a user
class CreateCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        collection_name = request.data.get('collection_name')
        if username and collection_name:
            try:
                user_service = UserService()
                user = user_service.get_user_by_username(username)
                collection_service = CollectionService()
                response_data, status_code = collection_service.create_collection(user, collection_name)
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error creating collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id or collection_name provided'}, status=400)


# Get collection data for a user by collection name
class GetCollectionView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.data.get('username')
        collection_name = request.data.get('collection_name')
        if username and collection_name:
            try:
                user_service = UserService()
                user = user_service.get_user_by_username(username)
                collection_service = CollectionService()
                card_list = collection_service.get_collection_by_name(user, collection_name)
                return Response(card_list, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error fetching collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id or collection_name provided'}, status=400)


# Get all collection data for a user
class GetCollectionsView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.data.get('username')
        if username:
            try:
                user_service = UserService()
                user = user_service.get_user_by_username(username)
                collection_service = CollectionService()
                card_list = collection_service.get_all_collections(user)
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
        logger.info(f"File: {csv_file}")
        action = request.data.get('action')
        logger.info(f"Action: {action}")
        username = request.data.get('username')
        logger.info(f"Username: {username}")
        collection_name = request.data.get('collection_name')
        logger.info(f"Collection Name: {collection_name}")

        if csv_file and username and collection_name:
            try:
                user_service = UserService()
                user = user_service.get_user_by_username(username)
                collection_service = CollectionService()
                scryfall_data, finish_map = collection_service.process_csv(csv_file)
                if action == 'update':
                    collection_service.clear_collection(user, collection_name)
                response_data, status_code = collection_service.add_collection(user, collection_name,
                                                                               scryfall_data, finish_map)
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No file, action, or discord_id provided'}, status=400)


# Delete collection data for a user
class DeleteCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        collection_name = request.data.get('collection_name')
        if username:
            try:
                user_service = UserService()
                user = user_service.get_user_by_username(username)
                collection_service = CollectionService()
                response_data, status_code = collection_service.delete_collection(user, collection_name)
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"Error clearing collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id provided'}, status=400)

