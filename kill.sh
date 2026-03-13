#!/bin/bash
source venv/bin/activate
ps aux | grep main.py
ps aux | grep bot.py
ps aux | grep app.py
ps aux | grep scheduler.py
pkill -f bot.py
pkill -f main.py
pkill -f app.py
pkill -f scheduler
docker stop todo_printer_container
docker rm todo_printer_container
sleep 1
