#!/bin/bash
source venv/bin/activate
ps aux | grep main.py
ps aux | grep bot.py
pkill -f bot.py
pkill -f main.py
sleep 1
