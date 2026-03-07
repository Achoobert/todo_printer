"""html from list - long multi-line test."""

import tempfile
import textwrap
from datetime import datetime
import logging
import random
import yaml
import os
import math

logger = logging.getLogger(__name__)

def to_html(task_data , current_date_text):

    task_html = ""
    title_total_height = 0
    mmPerLine = 10
    maxCharPerLine = 16

    for line in task_data.split('\n'):
        if line.strip():
            line = line.strip()
            linelen = len(line)
            # mmForThisLine 
            title_total_height += mmPerLine*(math.ceil(linelen/maxCharPerLine))
            task_html += f"<li>{line}</li>"

    # Calculate content height from html lines
    date_height = 7
    htmlheight = title_total_height  + date_height 
    # I want to see if it's better to calc here
   #  logger.info(f"htmlheight{htmlheight}")

    html_template = """<!DOCTYPE html>
<html>
<head>
   <style>
      @page {{ width: 80mm; height: {htmlheight}mm; margin: 1mm; }}

      body {{
         font-family: 'monospace', monospace;
         font-size: 14px;
         line-height: 1.5;
         /* Typical thermal printer width */
         margin: 0;
         padding: 0;
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
      <subtitle>{current_date_text}</subtitle>
      <ul>
         {task_html}
      </ul>
   </body>
   
   </html>
   """
    
    h = html_template.format(
        task_html=task_html,
        current_date_text=current_date_text,
        htmlheight=htmlheight
    )
   #  logger.info(f'{h}')
    return h

def create_list_html(task_data):
    """return task card html with emojis and a created date."""
    # current date 
    current_date = datetime.now().strftime("%B %d")
    day = int(datetime.now().strftime("%d"))
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    current_date_text = f"{datetime.now().strftime('%B %d')}{suffix}"

    return to_html(task_data , current_date_text)
