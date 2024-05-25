from django.apps import AppConfig
import threading


class DiscordBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discord_bot'

    def ready(self):
        from .bot import run_bot  # Import the bot's run function

        def start_bot():
            run_bot()

        thread = threading.Thread(target=start_bot)
        thread.start()
