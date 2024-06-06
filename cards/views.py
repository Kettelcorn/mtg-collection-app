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
from .models import Card, Collection, User



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

class GetCollectionView(APIView):
    def get(self, request, *args, **kwargs):
        discord_id = request.query_params.get('discord_id')
        if discord_id:
            try:
                user = User.objects.get(discord_id=discord_id)
                collection = user.collection
                cards = collection.cards.all()
                card_list = []
                for card in cards:
                    card_list.append({
                        'card_name': card.card_name,
                        'scryfall_id': card.scryfall_id,
                        'tcg_id': card.tcg_id,
                        'set': card.set,
                        'collector_number': card.collector_number,
                        'finish': card.finish,
                        'print_uri': card.print_uri,
                        'price': card.price,
                        'quantity': card.quantity
                    })
                return Response(card_list, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error fetching collection: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No discord_id provided'}, status=400)

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
                scryfall_data = []
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
                            scryfall_data.append(data)
                        else:
                            logger.error(f"Error fetching card details: {response.json()}")
                        time.sleep(0.2)

                logger.info(f"discord_id: {request.data.get('discord_id')}")
                user = User.objects.get(discord_id=request.data.get('discord_id'))
                collection = user.collection
                collection.cards.all().delete()

                for data in scryfall_data:
                    for selected_card in data.get('data'):
                        name = selected_card.get('name')
                        id = selected_card.get('id')
                        tcgplayer_id = selected_card.get('tcgplayer_id')
                        set_name = selected_card.get('set_name')
                        collector_number = selected_card.get('collector_number')
                        finish = None
                        if card['Printing'] == 'Normal':
                            finish = 'nonfoil'
                        elif card['Printing'] == 'Foil':
                            finish = 'foil'
                        uri = selected_card.get('uri')
                        price = None
                        if finish == 'foil':
                            price = selected_card.get('prices').get('usd_foil')
                        else:
                            price = selected_card.get('prices').get('usd')
                        quantity = card['Quantity']

                        card_obj = Card(
                            card_name=name,
                            scryfall_id=id,
                            tcg_id=tcgplayer_id,
                            set=set_name,
                            collector_number=collector_number,
                            finish=finish,
                            print_uri=uri,
                            collection=collection,
                            price=price,
                            quantity=quantity
                        )
                        card_obj.save()
                return Response({'message': 'Data received successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

