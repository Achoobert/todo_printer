import sys
import os

# Add the src directory to the Python path to allow importing daily_briefing_builder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from html_to_image import html_convert_to_image
from printer import print_image_to_printer 

tables = ["Crusaders","Wildcards","Saga","Carrotbottoms"]

with open("templates/lazy_gm.html", "r") as f:
    lazy_gm_content = f.read()
    for table in tables:
        lazy_gm_content = lazy_gm_content.replace("TABLE_NAME", table)
        html_output = html_convert_to_image(lazy_gm_content)
        print_image_to_printer(html_output)
