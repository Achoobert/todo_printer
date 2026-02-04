import os
import requests
import tempfile
import logging
logger = logging.getLogger(__name__)

from .html_to_image import html_convert_to_image, create_text_image
from .task_image_generator import create_short_task_image
from .llm_helper import expand_task
from .printer import print_text, print_image_to_printer # Renamed print_img to print_image_to_printer to avoid confusion

from PIL import Image
import io # Import io for in-memory image handling

def web_processor(message):
    task_content = message.get("content")
    logger.info(f"Received task content: {task_content}")

    if not task_content:
        logger.info("No task content received.")
        return

    if task_content.lower().startswith("<html>") and task_content.lower().endswith("</html>"):
        logger.info("Processing HTML content.")
        print_html(task_content)
    elif len(task_content) < 40:
        logger.info(f"Processing short task (length: {len(task_content)}).")
        image_obj = create_short_task_image(task_content, "MEDIUM")
        if image_obj:
            print_image_to_printer(image_obj)
    else:
        logger.info(f"Processing long task (length: {len(task_content)}).")
        # For longer text, place in HTML template, convert to PDF, then to image
        html_content = f"<html><body><p>{task_content}</p></body></html>"
        print_html(html_content)

async def bot_processor(message, client):
    """process incoming messages from discord"""
    if message.author == client.user:
        return
    if message.channel.name == "tasks":
        if message.content.strip().lower() == "lazy_gm":
            with open("templates/lazy_gm.html", "r") as f:
                lazy_gm_content = f.read()
            print_html(lazy_gm_content)
        elif message.content.strip().lower() == "tiny":
            with open("templates/tiny.html", "r") as f:
                tiny = f.read()
            print_html(tiny)
        else:
            # create_short_task_image should return a PIL Image object
            image_obj = create_short_task_image(message.content, priority="LOW")
            if image_obj:
                print_image_to_printer(image_obj)
    
    if message.channel.name == "lists":
        print_list(message.content)

    if message.channel.name == "prompt":
        prompt_to_list(message.content)

    if message.channel.name == "text":
        print_text_as_image(message.content)
    
    if message.channel.name == "img":
        if message.attachments:
            for attachment in message.attachments:
                if 'image' in attachment.content_type:
                    # Download image and convert to PIL Image object in memory
                    try:
                        response = requests.get(attachment.url)
                        response.raise_for_status()
                        img_data = io.BytesIO(response.content)
                        img = Image.open(img_data)
                        img = img.convert("1", dither=Image.FLOYDSTEINBERG)
                        print_image_to_printer(img)
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading image from {attachment.url}: {e}")
                    except Exception as e:
                        print(f"Error processing image: {e}")
                    break
        else:
            return "Please attach an image to print."

    if message.content.startswith('$hello'):
        return 'Hello!'

async def bot_direct(message, client):
    """process incoming messages from discord"""
    if message.author == client.user:
        return
    if message.channel.name == "tasks":
        # create_short_task_image should return a PIL Image object
        image_obj = create_short_task_image(message.content, priority="LOW")
        if image_obj:
            print_image_to_printer(image_obj)
    
    print_text_as_image(message.content)


def print_html(html):
    """Converts HTML into an image and prints it to the receipt printer."""
    # html_convert_to_image should return a PIL Image object
    image_obj = html_convert_to_image(html)
    if image_obj:
        print_image_to_printer(image_obj)

def print_list(text):
    checklist_version = ""
    for line in text.split('\n'):
        if line.strip():
            checklist_version += (f"[ ] {line.strip()}\n")
    print_text_as_image(checklist_version)

def print_text_as_image(text):
    # create_text_image should return a PIL Image object
    image_obj = create_text_image(text)
    if image_obj:
        print_image_to_printer(image_obj)
    else:
        # Fallback to text printing if image generation fails
        print_text(text)

def prompt_to_list(text):
    llm_output = expand_task(text)
    print_text_as_image(llm_output)
