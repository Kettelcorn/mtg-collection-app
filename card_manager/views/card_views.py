from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
import os
from dotenv import load_dotenv
from ..services.card_services import CardService


logger = logging.getLogger('card_manager')
load_dotenv()
# TODO: Remove scryfall urls from env file and other non-sensitive data


# Get card data from Scryfall API
class GetCardView(APIView):
    def get(self, request, *args, **kwargs):
        card_name = request.data.get('name')
        search_type = request.data.get('type')
        valid_users = request.data.get('valid_users', [])
        if card_name and search_type:
            try:
                card_service = CardService()
                card_details, status_code = card_service.fetch_card_details(card_name, search_type, valid_users)
                if status_code == 200:
                    logger.info(f"/api/get_card/: Card details retrieved: {card_name} {status.HTTP_200_OK}")
                    return Response(card_details, status=status.HTTP_200_OK)
                else:
                    logger.error(f"/api/get_card/: Card not found: {card_name} {status_code}")
                    return Response({'error': 'Card not found'}, status=status_code)
            except Exception as e:
                logger.error(f"/api/get_card/: Error fetching card: {e}")
                return Response({"detail": "An error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"/api/get_card/: No card name provided {status.HTTP_400_BAD_REQUEST}")
            return Response({'error': 'No card name provided'}, status=400)
