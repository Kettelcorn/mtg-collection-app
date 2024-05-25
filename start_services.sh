#!/bin/bash
# Start Django server
python manage.py runserver 0.0.0.0:8000 &

# Start Discord bot
python manage.py run_bot
