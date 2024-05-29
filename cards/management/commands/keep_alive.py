import logging
import os
import time
import requests
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Sends periodic requests to keep the server alive'

    def handle(self, *args, **kwargs):
        url = os.getenv('URL')
        logging.info(f"Sending keep-alive requests to {url}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(f"Successfully pinged {url}")
            else:
                logging.error(f"Failed to ping {url}")
        except Exception as e:
            logging.error(f"Error sending keep-alive request: {e}")