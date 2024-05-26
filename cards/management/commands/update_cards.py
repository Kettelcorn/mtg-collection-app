from django.core.management.base import BaseCommand
from cards.scryfall_bulk import get_bulk_data_download_uri, download_bulk_data, process_bulk_data
import tempfile
import logging

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Update cards from Scryfall bulk data'

    def handle(self, *args, **options):
        download_uri = get_bulk_data_download_uri()
        if not download_uri:
            self.stdout.write(self.style.ERROR('Failed to get download URI'))
            return

        bulk_data = download_bulk_data(download_uri)
        if not bulk_data:
            self.stdout.write(self.style.ERROR('Failed to download bulk data'))
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
            tmp_file.write(bulk_data)
            tmp_file.flush()
            process_bulk_data(tmp_file.name)

        self.stdout.write(self.style.SUCCESS('Successfully updated cards'))
