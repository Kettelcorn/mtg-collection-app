import json

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from dotenv import load_dotenv
import os
import logging
import pandas as pd
from requests_toolbelt.multipart.encoder import MultipartEncoder

logger = logging.getLogger(__name__)

load_dotenv()
API_URL = os.getenv('API_URL')
GET_CARD = os.getenv('GET_CARD')


# Test cases for the GetCardView API view
class GetCardViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = f"{API_URL}{GET_CARD}"

    # Test case for getting a card with a normal layout
    def test_get_card_normal(self):
        data = {
            'name': 'Sol Ring',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Sol Ring', response.data.get('name'))
        self.assertEqual('normal', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'image_uris', 'related_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a printing of a card
    def test_get_printing(self):
        data = {
            'name': 'Nicol Bolas, God-Pharaoh',
            'type': 'printing',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Nicol Bolas, God-Pharaoh', response.data.get('name'))
        self.assertIn('prints', response.data)
        self.assertIn('users', response.data)

    # Test case for creating a user, creating a collection, and adding a card to the collection, then getting the card
    def test_user_has_card(self):
        # Create a user
        data = {
            'username': 'test_user',
            'password': 'test_password',
            'discord_id': 'test_discord_id'
        }
        response = self.client.post(f"{API_URL}/api/create_user/",
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a collection for the user
        data = {
            'username': 'test_user',
            'collection_name': 'test_collection'
        }
        response = self.client.post(f"{API_URL}/api/create_collection/",
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Add cards to the collection
        update_collection_url = f"{API_URL}/api/update_collection/"
        current_dir = os.path.dirname(__file__)
        csv_file_path = os.path.join(current_dir, 'test_list.csv')
        with open(csv_file_path, 'rb') as csv_file:
            csv_file_content = csv_file.read()
        form = MultipartEncoder(
            fields={
                'username': 'test_user',
                'action': 'add',
                'collection_name': 'test_collection',
                'file': ('test_list.csv', csv_file_content, 'text/csv')
            }
        )
        response = self.client.post(update_collection_url, data=form.to_string(), content_type=form.content_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the card
        data = {
            'name': 'Bone Saw',
            'type': 'card',
            'valid_users': ['test_user']
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Bone Saw', response.data.get('name'))
        self.assertIn('users', response.data)
        self.assertEqual(1, len(response.data.get('users')))
        self.assertEqual('test_user', list(response.data.get('users').keys())[0])

    # Test case for getting a card with a double faced layout
    def test_get_card_double_face(self):
        data = {
            'name': 'Malakir Rebirth // Malakir Mire',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Malakir Rebirth // Malakir Mire', response.data.get('name'))
        self.assertEqual('modal_dfc', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'card_faces', 'related_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a card with a split layout
    def test_get_card_split(self):
        data = {
            'name': 'Fire // Ice',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Fire // Ice', response.data.get('name'))
        self.assertEqual('split', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'card_faces', 'related_uris', 'image_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a card with an adventure layout
    def test_get_card_adventure(self):
        data = {
            'name': 'Mosswood Dreadknight // Dread Whispers',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Mosswood Dreadknight // Dread Whispers', response.data.get('name'))
        self.assertEqual('adventure', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'card_faces', 'related_uris', 'image_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a card with a flip layout
    def test_get_card_flip(self):
        data = {
            'name': 'Bushi Tenderfoot // Kenzo the Hardhearted',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Bushi Tenderfoot // Kenzo the Hardhearted', response.data.get('name'))
        self.assertEqual('flip', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'card_faces', 'related_uris', 'image_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a card with a meld layout
    def test_get_card_meld(self):
        data = {
            'name': 'Mishra, Lost to Phyrexia',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Mishra, Lost to Phyrexia', response.data.get('name'))
        self.assertEqual('meld', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'related_uris', 'image_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    def test_get_card_emblem(self):
        data = {
            'name': 'Elspeth, Knight-Errant Emblem',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Elspeth, Knight-Errant Emblem', response.data.get('name'))
        self.assertEqual('emblem', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'related_uris', 'image_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a card with an invalid name
    def test_get_card_invalid_name(self):
        data = {
            'name': 'invalid card name',
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    # Test case for getting a card with no name
    def test_get_card_no_name(self):
        data = {
            'type': 'card',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Test case for getting a card with no type
    def test_get_card_no_type(self):
        data = {
            'name': 'invalid card name',
            'valid_users': []
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Test case for no valid users
    def test_get_card_no_valid_users(self):
        data = {
            'name': 'Sol Ring',
            'type': 'card'
        }
        response = self.client.generic('GET', self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('users', response.data)
    # TODO: Add test when user is created and has card you want

