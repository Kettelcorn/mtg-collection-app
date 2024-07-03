import json

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from dotenv import load_dotenv
import os
import logging

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

    # TODO: Add test for missing valid_users parameter
