from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from dotenv import load_dotenv
import os
import logging

load_dotenv()
API_URL = os.getenv('API_URL')
GET_CARD= os.getenv('GET_CARD')


# Test cases for the GetCardView API view
class GetCardViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = f"{API_URL}{GET_CARD}"

    # Test case for getting a card with a normal layout
    def test_get_card_normal(self):
        response = self.client.get(self.url, {'name': 'sol ring', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('normal', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'tcgplayer_id', 'image_uris', 'related_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    # Test case for getting a card with a double faced layout
    def test_get_card_double_face(self):
        response = self.client.get(self.url, {'name': 'Malakir Rebirth // Malakir Mire', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response = self.client.get(self.url, {'name': 'Fire // Ice', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response = self.client.get(self.url, {'name': 'Mosswood Dreadknight // Dread Whispers', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response = self.client.get(self.url, {'name': 'Bushi Tenderfoot // Kenzo the Hardhearted', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response = self.client.get(self.url, {'name': 'Mishra, Lost to Phyrexia', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('meld', response.data.get('layout'))
        expected_fields = [
            'id', 'name', 'uri', 'prints_search_uri', 'users', 'released_at', 'set_name', 'collector_number', 'prices',
            'finishes', 'related_uris', 'image_uris'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    def test_get_card_emblem(self):
        response = self.client.get(self.url, {'name': 'Elspeth, Knight-Errant Emblem', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response = self.client.get(self.url, {'name': 'invalid card name', 'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    # Test case for getting a card with no name
    def test_get_card_no_name(self):
        response = self.client.get(self.url, {'type': 'card'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Test case for getting a card with no type
    def test_get_card_no_type(self):
        response = self.client.get(self.url, {'name': 'Sol Ring'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
