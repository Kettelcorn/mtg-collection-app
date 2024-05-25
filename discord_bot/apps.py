from django.apps import AppConfig
import threading


class DiscordBotConfig(AppConfig):
    name = 'discord_bot'

    def ready(self):
        if not hasattr(self, 'started'):
            self.started = True
            from .bot import run_bot  # Import the bot's run function

            def start_bot():
                run_bot()

            thread = threading.Thread(target=start_bot)
            thread.start()
