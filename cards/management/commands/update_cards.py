from django.core.management.base import BaseCommand
from cards.scryfall_bulk import get_bulk_data_download_uri, download_and_process_bulk_data, process_bulk_data
import logging

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Update cards from Scryfall bulk data'

    def handle(self, *args, **options):
        download_uri = get_bulk_data_download_uri()
        logging.info(f'Download URI: {download_uri}')
        if not download_uri:
            logging.error('Failed to get download URI')
            self.stdout.write(self.style.ERROR('Failed to get download URI'))
            return

        download_and_process_bulk_data(download_uri)
        logging.info('Successfully updated cards')
        self.stdout.write(self.style.SUCCESS('Successfully updated cards'))
