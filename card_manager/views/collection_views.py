from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..services.collection_services import CollectionService
from ..services.user_services import UserService

logger = logging.getLogger('card_manager')

# TODO: Figure out how to authenticate users when using this API


# Create a collection for a user
class CreateCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        collection_name = request.data.get('collection_name')
        if username and collection_name:
            try:
                user_service = UserService()
                user = user_service.get_user_by_username(username)
                collection_service = CollectionService()
                response_data, status_code = collection_service.create_collection(user, collection_name)
                logger.info(
                    f"/api/create_collection/: Collection created for {username}: {collection_name} {status_code}"
                )
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"/api/create_collection/: Error creating collection for {username}: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(
                f"/api/create_collection/: No username or collection_name provided {status.HTTP_400_BAD_REQUEST}"
            )
            return Response({'error': 'No username or collection_name provided'}, status=400)


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
                logger.info(
                    f"/api/get_collection/: Collection retrieved for {username}: {collection_name} {status.HTTP_200_OK}"
                )
                return Response(card_list, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"/api/get_collection/: Error fetching collection for {username}: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"/api/get_collection/: No username or collection_name provided {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'No username or collection_name provided'}, status=400)


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
                logger.info(f"/api/get_collections/: All collections retrieved for {username} {status.HTTP_200_OK}")
                return Response(card_list, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"/api/get_collections/: Error fetching collections for {username}: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"/api/get_collections/: No username provided {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'No username provided'}, status=400)


# Update collection data for a user
class UpdateCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        action = request.data.get('action')
        username = request.data.get('username')
        collection_name = request.data.get('collection_name')

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
                logger.info(
                    f"/api/update_collection/: Collection updated for {username}: {collection_name} {status_code}"
                )
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"/api/update_collection/: Error updating collection for {username}: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(
                f"/api/update_collection/: No file, action, or username provided {status.HTTP_400_BAD_REQUEST}"
            )
            return Response({'error': 'No file, action, or username provided'}, status=400)


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
                logger.info(
                    f"/api/delete_collection/: Collection deleted for {username}: {collection_name} {status_code}"
                )
                return Response(response_data, status=status_code)
            except Exception as e:
                logger.error(f"/api/delete_collection/: Error deleting collection for {username}: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"/api/delete_collection/: No username provided {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'No username provided'}, status=400)

