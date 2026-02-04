from flask import Flask, render_template, request
from .message_router import web_processor

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("../templates/index.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.is_json:
        data = request.get_json()
        web_processor(data)
        return "Task submitted and sent to printer!", 200
    return "Error: Request must be JSON.", 400

@app.route("/apple-shortcut-task", methods=["POST"])
def apple_shortcut_task():
    if request.is_json:
        data = request.get_json()
        task_content = data.get("task")
        if task_content:
            web_processor({"content": task_content, "source": "apple_shortcut"})
            return "Task received from Apple Shortcut and sent to printer!", 200
        return "Error: 'task' field missing in JSON payload.", 400
    return "Error: Request must be JSON.", 400

@app.route("/add-garbage-item", methods=["POST"])
def add_garbage_item():
    if request.is_json:
        data = request.get_json()
        item = data.get("item")
        if item:
            from lists import add_item_to_list
            add_item_to_list("garbage", item)
            return "Garbage item added!", 200
        return "Error: 'item' field missing in JSON payload.", 400
    return "Error: Request must be JSON.", 400

@app.route("/add-dream-item", methods=["POST"])
def add_dream_item():
    if request.is_json:
        data = request.get_json()
        item = data.get("item")
        if item:
            from lists import add_item_to_list
            add_item_to_list("dream", item)
            return "Dream item added!", 200
        return "Error: 'item' field missing in JSON payload.", 400
    return "Error: Request must be JSON.", 400

@app.route("/print-list/", methods=["POST"])
def print_specific_list(list_name):
    from lists import get_list_content, clear_list
    from message_router import print_list as router_print_list
    
    content = get_list_content(list_name)
    if content:
        list_text = f"--- {list_name.capitalize()} List ---\n" + "\n".join(content)
        router_print_list(list_text)
        clear_list(list_name) # Clear after printing
        return f"{list_name.capitalize()} list printed and cleared!", 200
    return f"No items in {list_name.capitalize()} list to print.", 200

import logging

logger = logging.getLogger(__name__)

def start():
    logger.info("Attempting to start Flask app.")
    try:
        app.run(host="0.0.0.0", port=8444)
        logger.info("Flask app started successfully.")
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
