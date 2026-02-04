import json
import os
from datetime import datetime

LISTS_FILE = "lists.json"

def _load_lists():
    if os.path.exists(LISTS_FILE):
        with open(LISTS_FILE, "r") as f:
            return json.load(f)
    return {"garbage": [], "dream": []}

def _save_lists(lists):
    with open(LISTS_FILE, "w") as f:
        json.dump(lists, f, indent=2)

def add_item_to_list(list_name, item):
    lists = _load_lists()
    if list_name in lists:
        lists[list_name].append({"item": item, "timestamp": datetime.now().isoformat()})
        _save_lists(lists)
        return True
    return False

def get_list_content(list_name):
    lists = _load_lists()
    return [item["item"] for item in lists.get(list_name, [])]

def clear_list(list_name):
    lists = _load_lists()
    if list_name in lists:
        lists[list_name] = []
        _save_lists(lists)
        return True
    return False
