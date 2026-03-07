"""Image generation for task cards."""

import tempfile
import textwrap
from datetime import datetime
import logging
import random
import yaml
import os
import math

logger = logging.getLogger(__name__)

def to_html(task_data , due_date_text, emoji_text):

    title_total_height = 0
    mmPerLine = 18
    maxCharPerLine = 11

    task_html = ""
    for line in task_data.split('\n'):
        if line.strip():
            line = line.strip()
            linelen = len(line)
            # mmForThisLine 
            title_total_height += mmPerLine*(math.ceil(linelen/maxCharPerLine))
            task_html += f"{line}</br>"

    # Calculate content height from html lines
    date_height = 10
    # min height is 60
    htmlheight = max( (title_total_height + date_height), 60)
    # I want to see if it's better to calc here
    logger.info(f"htmlheight{title_total_height + date_height}")

    html_template = """<!DOCTYPE html>
<html>
<head>
   <style>
      @page {{ width: 80mm; height: {htmlheight}mm; margin: 1mm; }}

      body {{
         font-family: 'monospace', monospace;
         font-size: 45px;
         line-height: 1.1;
         /* Typical thermal printer width */
         margin: 0;
         padding: 0;
         text-align: center;
      }}

      h1 {{
         text-align: center;
         display: inline;
         font-size: 50px;
      }}

      h2 {{
         text-align: center;
         font-size: 38px;
      }}

      subtitle {{
         text-align: center;
         display: inline;
         font-size: 10px;
         margin-top: 0px;
         margin-bottom: 0px;
      }}
   </style>
   </head>
   
   <body>
      <div>{task_html}</div>
      </br>
         <h1>{emoji_text}</h1>
      <subtitle>{due_date_text}</subtitle>
         <h1>{emoji_text}</h1>
   </body>
   
   </html>
   """
    
    h = html_template.format(
        task_html=task_html,
        due_date_text=due_date_text,
        emoji_text=emoji_text,
        htmlheight=htmlheight
    )
   #  logger.info(f'{h}')
    return h

def create_short_task_html(task_data, priority="LOW"):
    """return task card html with emojis and a created date."""
    # If no font found, use default
    # 🔜 ⚒️⛔️🔧🟰🧰🧱🧲🧳🧴🧵🧶🧷🧸🧹🧺🧻🧼🧽🧾 🧿♠️♣️♥️♦️♨️⛏️
    #  ☠️ ⚠️ ‼ ⚒️♠️♣️♥️♦️♨️
    # if priority.upper() == "HIGH":
    #     # Three lightning bolt emojis
    #     emoji_text = "⚠️ ⚡ ⚠️"
    # else:
        # Single lightning bolt emoji
    random_symbol_list = [ "♨️","☠️", "⚠️", "‼","⚡","🔜","⚒️","⛔️","♠️","♣️","♥️","♦️","♥️" ]
    picker = random.randint(0, len(random_symbol_list))
    emoji_text = random_symbol_list[picker]
    # due date
    due_date = datetime.now().strftime("%B %d")
    day = int(datetime.now().strftime("%d"))
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    due_date_text = f"{datetime.now().strftime('%B %d')}{suffix}"

    html_version = to_html(task_data , due_date_text, emoji_text)

    return html_version
