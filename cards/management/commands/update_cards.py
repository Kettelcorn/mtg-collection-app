from django.core.management.base import BaseCommand
from cards.scryfall_bulk import get_bulk_data_download_uri, download_bulk_data, process_bulk_data
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

        bulk_data = download_bulk_data(download_uri)
        logging.info(f'First 100 bytes of bulk data: {bulk_data[:100]}')
        if not bulk_data:
            logging.error('Failed to download bulk data')
            self.stdout.write(self.style.ERROR('Failed to download bulk data'))
            return

        process_bulk_data(bulk_data)
        logging.info('Successfully updated cards')
        self.stdout.write(self.style.SUCCESS('Successfully updated cards'))
