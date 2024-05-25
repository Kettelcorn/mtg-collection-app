from django.core.management.base import BaseCommand
from discord_bot.bot import run_bot


class Command(BaseCommand):
    help = 'Run the Discord bot'

    def handle(self, *args, **options):
        run_bot()
