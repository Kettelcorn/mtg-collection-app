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
from decimal import Decimal



logger = logging.getLogger(__name__)
load_dotenv()
SCRYFALL_URL = os.getenv('SCRYFALL_URL')


# Gets card details from Scryfall API
class GetCardView(APIView):
    def get(self, request, *args, **kwargs):
        card_name = request.query_params.get('name')
        search_type = request.query_params.get('type')
        if card_name:
            try:
                params = {
                    'fuzzy': card_name,
                }
                response = requests.get(SCRYFALL_URL, params=params)
                if response.status_code == 200:
<<<<<<< HEAD
                    users = []
=======
                    logger.info(f"Card details fetched")
                    users = {}
>>>>>>> 97cf014e947698d207a268052bc30122ea918f6f
                    card_details = response.json()

                    for user in User.objects.all():
                        collection = user.collection
                        cards = collection.cards.filter(card_name=card_name)
                        logger.info(type(cards))
                        if cards:
                            for card in cards:
                                logger.info(f"card: {card}{type(card)}")
                                if user.discord_username not in users:
                                    users[user.discord_username] = []
                                users[user.discord_username].append(
                                        {
                                            "username": user.discord_username,
                                            "set": card.set,
                                            "collector_number": card.collector_number,
                                            "finish": card.finish,
                                            "price": card.price,
                                            "tcg_id": card.tcg_id,
                                            "quantity": card.quantity
                                        }
                                )
                    card_details['users'] = users
                    if search_type == 'printing':
                        print_search_uri = card_details.get('prints_search_uri')
                        if print_search_uri:
                            print_response = requests.get(print_search_uri)
                            if print_response.status_code == 200:
                                card_details['prints'] = print_response.json().get('data', [])
                            else:
                                logger.warning(f"Error fetching print data: {print_response.json()}")
                        return Response(card_details, status=status.HTTP_200_OK)
                    elif search_type == 'card':
                        return Response(card_details, status=status.HTTP_200_OK)
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
                total_value = Decimal(0.00)
                total_quantity = 0
                for card in cards:
                    card_list.append(
                        {
                            'card_name': card.card_name,
                            'scryfall_id': card.scryfall_id,
                            'tcg_id': card.tcg_id,
                            'set': card.set,
                            'collector_number': card.collector_number,
                            'finish': card.finish,
                            'print_uri': card.print_uri,
                            'price': card.price,
                            'quantity': card.quantity
                        }
                    )
                    total_value += card.price * card.quantity
                    total_quantity += card.quantity
                card_list.insert(0,{"card_count": total_quantity, "total_value": total_value})
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
                total_quantity = 0
                total_sent = 0
                total_received = 0
                for card in card_list:
                    total_quantity += int(card['Quantity'])
                    collector_number = None
                    set_code = None
                    # the if checks are to handle different formats of the csv file
                    if 'Card Number' in card:
                        collector_number = card['Card Number']
                    elif 'Collector number' in card:
                        collector_number = card['Collector number']
                    if 'Set Code' in card:
                        set_code = card['Set Code']
                    if 'Set code' in card:
                        set_code = card['Set code']
                    identifiers.append(
                        {
                            'collector_number': collector_number,
                            'set': set_code
                        }
                    )
                    count += 1
                    if len(identifiers) == 75 or count == len(card_list):
                        logger.info(f"Identifiers length: {len(identifiers)}")
                        total_sent += len(identifiers)
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
                        identifiers = []
                        time.sleep(0.1)
                logger.info(f"Total quantity in csv: {total_quantity}")
                logger.info(f"Total sent to Scryfall: {total_sent}")
                logger.info(f"discord_id: {request.data.get('discord_id')}")
                user = User.objects.get(discord_id=request.data.get('discord_id'))
                collection = user.collection
                collection.cards.all().delete()

                index = 0
                for data in scryfall_data:
                    for selected_card in data.get('data'):
                        name = selected_card.get('name')
                        id = selected_card.get('id')
                        tcgplayer_id = selected_card.get('tcgplayer_id')
                        if tcgplayer_id is None:
                            tcgplayer_id = 0
                        set_name = selected_card.get('set_name')
                        collector_number = selected_card.get('collector_number')
                        finish = None
                        if 'Foil' in card_list[index]:
                            if card_list[index]['Foil'] == 'normal':
                                finish = 'nonfoil'
                            elif card_list[index]['Foil'] == 'foil':
                                finish = 'foil'
                            elif card_list[index]['Foil'] == 'etched':
                                finish = 'etched'
                        elif 'Printing' in card_list[index]:
                            if card_list[index]['Printing'] == 'Normal':
                                finish = 'nonfoil'
                            elif card_list[index]['Printing'] == 'Foil':
                                for finish in selected_card.get('finishes'):
                                    if finish == 'etched':
                                        finish = 'etched'
                                    elif finish == 'foil':
                                        finish = 'foil'
                                        break

                        if finish is None:
                            finish = 'none'
                        logger.info(f"Finish: {finish}")
                        uri = selected_card.get('uri')
                        price = None
                        if finish == 'foil':
                            price = selected_card.get('prices').get('usd_foil')
                        elif finish == 'nonfoil':
                            price = selected_card.get('prices').get('usd')
                        elif finish == 'etched':
                            price = selected_card.get('prices').get('usd_etched')
                        if price is None:
                            price = Decimal(0.00)
                        quantity = card_list[index]['Quantity']

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
                        index += 1
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

