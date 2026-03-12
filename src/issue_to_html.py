"""HTML for GitHub issue receipt cards."""

import re
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)


def markdown_to_plain(text):
    """Strip markdown syntax to plain text (no new deps). Bare URLs removed for paper output."""
    if not text:
        return ""
    s = text.strip()
    # Bare URLs (unclickable on paper) -> remove
    s = re.sub(r"https?://[^\s]+", "", s)
    # Remove code fences and inline code
    s = re.sub(r"`[^`]*`", "", s)
    s = re.sub(r"```[\s\S]*?```", "", s)
    # Headers: # ## ### -> remove
    s = re.sub(r"^#{1,6}\s*", "", s, flags=re.MULTILINE)
    # Bold/italic
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"__([^_]+)__", r"\1", s)
    s = re.sub(r"_([^_]+)_", r"\1", s)
    # Links: [text](url) -> text
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    # List markers
    s = re.sub(r"^\s*[-*+]\s+", "", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*\d+\.\s+", "", s, flags=re.MULTILINE)
    # Collapse multiple spaces/newlines left after URL removal
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def to_html(repo, task_data, date_text, title):
    task_html = ""
    title_total_height = 0
    mmHeaderHeight = 18
    mmPerLine = 10
    maxCharPerLine = 16

    for line in task_data.split("\n"):
        if line.strip():
            line = markdown_to_plain(line)
            if not line:
                continue
            linelen = len(line)
            title_total_height += mmPerLine * (math.ceil(linelen / maxCharPerLine))
            task_html += f"<li>{line}</li>"

    date_height = 7
    htmlheight = mmHeaderHeight + title_total_height + date_height

    subtitle_text = f"{repo}: {date_text}" if repo else date_text

    html_template = """<!DOCTYPE html>
<html>
<head>
   <style>
      @page {{ width: 80mm; height: {htmlheight}mm; margin: 1mm; }}

      body {{
         font-family: 'monospace', monospace;
         font-size: 14px;
         line-height: 1.5;
         margin: 0;
         padding: 0;
      }}

      h1 {{
         text-align: center;
         display: inline;
         font-size: 38px;
      }}

      subtitle {{
         text-align: center;
         display: block;
         font-size: 10px;
         font-weight: bold;
         margin-top: 3px;
         margin-bottom: 3px;
      }}

      ul {{
         list-style-type: none;
         padding: 0;
         margin: 0;
      }}

      li {{
         margin-bottom: 2px;
         font-size: 25px;
      }}

   </style>
   </head>
   <body>
      <h1>{title}</h1>
      <subtitle>{subtitle_text}</subtitle>
      <ul>
         {task_html}
      </ul>
   </body>
   </html>
   """

    return html_template.format(
        subtitle_text=subtitle_text,
        task_html=task_html,
        htmlheight=htmlheight,
        title=title,
    )


def _date_text_from_created_at(created_at):
    """Format created_at (ISO string or None) to 'Month Ddth'."""
    if created_at:
        try:
            if isinstance(created_at, str) and "T" in created_at:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                dt = created_at
            day = dt.day
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]
            return f"{dt.strftime('%B %d')}{suffix}"
        except (ValueError, TypeError):
            pass
    now = datetime.now()
    day = int(now.strftime("%d"))
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return f"{now.strftime('%B %d')}{suffix}"


def create_github_issue_html(repo=None, body=None, created_at=None, title=None):
    """Build issue receipt HTML. Supports (repo, body, created_at, title) or single body string for backward compat."""
    if body is None and repo is not None and title is None and created_at is None:
        body = repo
        repo = None
    body = body or ""
    date_text = _date_text_from_created_at(created_at)
    subtitle_repo = repo or ""
    if title and subtitle_repo:
        subtitle_repo = f"{subtitle_repo}"
    elif title:
        subtitle_repo = title
    return to_html(subtitle_repo, body, date_text, title)
