#!/bin/bash

# Function to start Django server
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!
echo "Django server started with PID $DJANGO_PID"

# Function to start Discord bot
python manage.py run_bot &
DISCORD_PID=$!
echo "Discord bot started with PID $DISCORD_PID"

# Trap SIGINT (Ctrl+C) and SIGTERM to stop both processes
trap 'kill $DJANGO_PID $DISCORD_PID' SIGINT SIGTERM

# Wait for both processes to complete
wait $DJANGO_PID $DISCORD_PID

