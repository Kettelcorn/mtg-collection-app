from django.core.management.base import BaseCommand
from cards.models import Card

class Command(BaseCommand):
    help = 'Count the number of cards in the database'

    def handle(self, *args, **options):
        card_count = Card.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Card count: {card_count}'))

