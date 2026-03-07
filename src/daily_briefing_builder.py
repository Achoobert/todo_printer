import logging
import datetime
import random
import yaml
import os

logger = logging.getLogger(__name__)

def daily_briefing(discord_goals_text):
    # Load configuration from YAML file
   #  logger.info(f'Load configuration from YAML file')/
    config_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'my_helpful_daily.yml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Parse deadline
    deadline_str = config['deadline']
    # Assuming deadline is in "day, month, year" format
    day, month, year = map(int, deadline_str.split(','))
    deadline_date = datetime.date(year, month, day)

    # Calculate days remaining
    today = datetime.date.today()
    days_remaining = (deadline_date - today).days

    # Calculate hours remaining
    minutes_per_day = config['minutesPerDay']
    total_minutes_remaining = days_remaining * minutes_per_day
    hours_remaining = total_minutes_remaining / 60

    # Select a random motivational phrase
    phrases = config['phrases']
    random_quote = random.choice(phrases)

   #  logger.info(f'random_quote: {random_quote} hours_remaining: {hours_remaining} days_remaining: {days_remaining}')    

    # Format goals for HTML
   #  logger.info(f'Format goals for HTML')
   #  goals_html = discord_goals_text.replace( '\n', "</li><li>")
    goals_html = ""
    for line in discord_goals_text.split('\n'):
        if line.strip():
            goals_html += f"<li>{line.strip()}</li>"
   #  logger.info(f' HTML {goals_html}')

    # HTML template
    html_template = """<!DOCTYPE html>
<html>
<head>
   <style>
      @page {{ width: 80mm; height: 70mm; margin: 1mm; }}

      body {{
         font-family: 'monospace', monospace;
         font-size: 14px;
         line-height: 1.5;
         /* Typical thermal printer width */
         margin: 0;
         padding: 0;
      }}

      h1 {{
         text-align: center;
         font-size: 25px;
      }}

      subtitle {{
         display: block;
         text-align: center;
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
      }}

   </style>
   
   </head>
   
   <body>
      <h1>{hours_remaining:.2f} hours</br>{days_remaining} days</h1>
      <subtitle>{random_quote}</subtitle>
      <ul>
         {goals_html}
      </ul>
   </body>
   
   </html>
   """
    
    h = html_template.format(
        days_remaining=days_remaining,
        hours_remaining=hours_remaining,
        random_quote=random_quote,
        goals_html=goals_html
    )
   #  logger.info(f'{h}')
    return h
