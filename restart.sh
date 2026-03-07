#!/bin/bash
# source my_custom.env

source venv/bin/activate
ps aux | grep main.py
ps aux | grep bot.py
pkill -f bot.py
pkill -f main.py
sleep 1


source venv/bin/activate
sleep 1
nohup python3 main.py &
