from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Card
from .serializers import CardSerializer
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class CardNameView(APIView):
    def get(self, request, *args, **kwargs):
        card_name = request.query_params.get('name')
        if card_name:
            try:
                card = Card.objects.filter(name__exact=card_name)
                if card.exists():
                    serializer = CardSerializer(card, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Card not found'}, status=404)
            except Exception as e:
                logger.error(f"Error fetching card details: {e}")
                return Response({"detail": "An error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No card name provided'}, status=400)


class UpdateCardsView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            logger.inf('Updating cards...')
            call_command('update_cards')
            return Response({'detail': 'Cards updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating cards: {e}", exc_info=True)
            return Response({'detail': 'Failed to update cards'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
