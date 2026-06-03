#!/bin/bash
# DISCORD_API_TOKEN must be set (e.g. in .env or my_custom.env). Source one of them:
[ -f .env ] && source .env
[ -f my_custom.env ] && source my_custom.env

source venv/bin/activate
ps aux | grep main.py
ps aux | grep bot.py
pkill -f bot.py
pkill -f main.py
sleep 1

nohup python3 main.py &
