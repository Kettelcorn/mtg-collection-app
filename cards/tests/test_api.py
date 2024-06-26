import time
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
import requests
from dotenv import load_dotenv
import os

load_dotenv()
GET_CARD_URL = os.getenv('GET_CARD_URL')


class GetCardViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse(GET_CARD_URL)

    # def test_get_card_details(self):
