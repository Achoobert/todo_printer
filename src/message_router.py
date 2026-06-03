import os
import re
import requests
import tempfile
import logging

logger = logging.getLogger(__name__)

_IMG_CHANNEL_MAX_BYTES = 10 * 1024 * 1024
_IMG_CHANNEL_REQUEST_TIMEOUT = 30
_IMG_CHANNEL_UA = {"User-Agent": "todo_printer/1.0"}
_URL_IN_TEXT_RE = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)

from .html_to_image import html_convert_to_image, create_text_image
from .short_task import create_short_task_html
from .medium_list import create_list_html
from .issue_to_html import create_github_issue_html
from .daily_briefing_builder import daily_briefing
from .llm_helper import expand_task
# Lazy import of schedule_trigger_thread in triggered_thread() to avoid circular import with bot
from .printer import print_text, print_image_to_printer # Renamed print_img to print_image_to_printer to avoid confusion

from PIL import Image
import io  # Import io for in-memory image handling


def _trim_trailing_url_chars(url: str) -> str:
    return url.rstrip(").,]'\"")


def _collect_img_channel_candidate_urls(message):
    """Ordered URLs: attachments, embed image/thumbnail/url, then bare http(s) in content. Deduped."""
    seen = set()
    out = []

    def add(u):
        if not u or not isinstance(u, str):
            return
        u = _trim_trailing_url_chars(u.strip())
        if not u.startswith(("http://", "https://")):
            return
        if u in seen:
            return
        seen.add(u)
        out.append(u)

    for att in message.attachments:
        add(att.url)
    for emb in message.embeds:
        if emb.image and emb.image.url:
            add(emb.image.url)
        if emb.thumbnail and emb.thumbnail.url:
            add(emb.thumbnail.url)
        if emb.url:
            add(emb.url)
    for m in _URL_IN_TEXT_RE.findall(message.content or ""):
        add(m)
    return out


def _download_image_bytes_capped(url):
    r = requests.get(
        url,
        headers=_IMG_CHANNEL_UA,
        timeout=_IMG_CHANNEL_REQUEST_TIMEOUT,
        stream=True,
    )
    r.raise_for_status()
    buf = io.BytesIO()
    total = 0
    for chunk in r.iter_content(chunk_size=65536):
        if not chunk:
            continue
        total += len(chunk)
        if total > _IMG_CHANNEL_MAX_BYTES:
            raise ValueError(
                f"response larger than {_IMG_CHANNEL_MAX_BYTES} bytes, aborting"
            )
        buf.write(chunk)
    return buf.getvalue()


def _normalize_for_bw_print(pil_img):
    img = pil_img
    if img.mode == "P" and "transparency" in img.info:
        img = img.convert("RGBA")
    if img.mode in ("RGBA", "LA"):
        base = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            base.paste(img, mask=img.split()[3])
        else:
            base.paste(img, mask=img.split()[1])
        img = base
    else:
        img = img.convert("RGB")
    return img.convert("1", dither=Image.FLOYDSTEINBERG)


def try_print_image_from_url(url: str) -> bool:
    try:
        data = _download_image_bytes_capped(url)
        bio = io.BytesIO(data)
        img = Image.open(bio)
        img.load()
        bw = _normalize_for_bw_print(img)
        print_image_to_printer(bw)
        return True
    except Exception as e:
        logger.warning("img channel: failed url=%s err=%s", url, e)
        return False


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
        short_task_html = create_short_task_html(task_content, priority="LOW")
        print_html(short_task_html)
    else:
        logger.info(f"Processing long task (length: {len(task_content)}).")
        # For longer text, place in HTML template, convert to PDF, then to image
        print_html(create_list_html(task_content))

async def bot_processor(message, client):
    """process incoming messages from discord"""
    if message.author == client.user:
        return
    if message.channel.name == "tasks":
        if message.content.strip().lower() == "lazy_gm":
            with open("templates/lazy_gm.html", "r") as f:
                lazy_gm_content = f.read()
            print_html(lazy_gm_content)
        else:
            short_task_html = create_short_task_html(message.content, priority="LOW")
            print_html(short_task_html)

    if message.channel.name == "goals":
        b_html = daily_briefing(message.content)
        print_html(b_html)

    if message.channel.name == "lists":
        print_list(message.content)

    if message.channel.name == "prompt":
        prompt_to_list(message.content)

    if message.channel.name == "text":
        print_text_as_image(message.content)
    
    if message.channel.name == "img":
        candidates = _collect_img_channel_candidate_urls(message)
        if not candidates:
            logger.info("img channel: no image URLs or attachments on message")
        else:
            for url in candidates:
                if try_print_image_from_url(url):
                    break
            else:
                logger.info(
                    "img channel: all candidates failed message_id=%s",
                    getattr(message, "id", None),
                )

    if message.content.startswith('$hello'):
        return 'Hello!'

async def bot_direct(message, client):
    """process incoming messages from discord"""
    if message.author == client.user:
        return
    if message.channel.name == "tasks":
        short_task_html = create_short_task_html(message.content, priority="LOW")
        print_html(short_task_html)
    
    if message.channel.name == "goals" or message.channel.name == "morning":
        # logger.info(f"Processing  message from goals")
        b_html = daily_briefing(message.content)
        print_html(b_html)
    else:
        print_text_as_image(message.content)

async def bot_direct_daily_briefing(message):
    """process incoming request for daily_briefing, whcih includes current goal-text from discord"""
    # create html, send to HTML printer
    b_html = daily_briefing(message.content)
    print_html(b_html)

def triggered_thread(thread_name):
    """Schedule fetching the latest message from the given Discord thread and processing it. Returns True if scheduled, False if bot not ready."""
    from .bot import schedule_trigger_thread
    return schedule_trigger_thread(thread_name)


def issue_processor(message):
    repo = message.get("repo")
    title = message.get("title")
    body = message.get("body")
    created_at = message.get("createdAt") or message.get("created_at")
    content = message.get("content")

    has_structured = repo or title or body
    if has_structured:
        html = create_github_issue_html(
            repo=repo or "",
            body=body or "",
            created_at=created_at,
            title=title,
        )
        logger.info("Processing GitHub issue (structured payload).")
        print_html(html)
        return
    if content:
        logger.info("Processing GitHub issue (content-only payload).")
        print_html(create_github_issue_html(content))
        return
    logger.info("No task content or structured issue fields received.")

def print_lazy_gm():
    tables = ["Crusaders","Wildcards","Saga","Carrotbottoms"]
    with open("lazy_gm.html", "r") as f:
        lazy_gm_content = f.read()
        for table in tables:
            lazy_gm_content = lazy_gm_content.replace("TABLE_NAME", table)
            html_output = html_convert_to_image(lazy_gm_content)
            print_image_to_printer(html_output)


def print_html(html):
    """Converts HTML into an image and prints it to the receipt printer."""
    # html_convert_to_image should return a PIL Image object
    image_obj = html_convert_to_image(html)
    if image_obj:
        print_image_to_printer(image_obj)

def print_list(text):
    print_html(create_list_html(text))
    # checklist_version = ""
    # for line in text.split('\n'):
    #     if line.strip():
    #         checklist_version += (f"[ ] {line.strip()}\n")
    # print_text_as_image(checklist_version)

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
