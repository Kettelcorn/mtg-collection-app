from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
import os
from dotenv import load_dotenv
import requests
from .models import User
from .serializers import UserSerializer
import csv
import json
import time



logger = logging.getLogger(__name__)
load_dotenv()
SCRYFALL_URL = os.getenv('SCRYFALL_URL')


# Gets card details from Scryfall API
class GetCardView(APIView):
    def get(self, request, *args, **kwargs):
        card_name = request.query_params.get('name')
        if card_name:
            try:
                params = {
                    'fuzzy': card_name,
                }
                response = requests.get(SCRYFALL_URL, params=params)
                if response.status_code == 200:
                    logger.info(f"Card details fetched")
                    response = requests.get(response.json().get('prints_search_uri'))
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Card not found'}, response.status_code)
            except Exception as e:
                logger.error(f"Error fetching card details: {e}")
                return Response({"detail": "An error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No card name provided'}, status=400)


class UpdateCollectionView(APIView):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        action = request.data.get('action')

        if csv_file and action:
            logger.info(f"File received: {csv_file.name}")
            try:
                url = "https://api.scryfall.com/cards/collection"
                headers = {
                    "Content-Type": "application/json"
                }
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                card_list = [row for row in reader]
                logger.info(f"{len(card_list)} cards found")
                identifiers = []
                count = 0
                for card in card_list:
                    collector_number = card['Card Number']
                    set_code = card['Set Code']
                    identifiers.append(
                        {
                            'collector_number': collector_number,
                            'set': set_code
                        }
                    )
                    count += 1
                    if len(identifiers) == 75 or count == len(card_list):
                        body = {
                            "identifiers": identifiers
                        }
                        response = requests.post(url, headers=headers, data=json.dumps(body))
                        if response.status_code == 200:
                            logger.info(f"Card details fetched")
                            data = response.json()
                            for card in data.get('data'):
                                logger.info(f"Card found: {card.get('name')}")
                        else:
                            logger.error(f"Error fetching card details: {response.json()}")
                        identifiers = []
                        time.sleep(0.2)
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message': 'Data received successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No file or action provided'}, status=400)


class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Ping view to check if the server is running
class PingView(APIView):
    def post(self, request, *args, **kwargs):
        response_data = {'message': 'Data received successfully'}
        return Response(response_data, status=status.HTTP_200_OK)

