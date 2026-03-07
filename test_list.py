import sys
import os

# Add the src directory to the Python path to allow importing daily_briefing_builder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from medium_list import create_list_html

# Test data
test_goals = "Test item Onethatgoes onand on and on and on and on and on and on and on\nTest item Two\nTest item Three\nTest item One\nTest item Two\nTest item Three"

# Call the function
html_output = create_list_html(test_goals)

# Print the output
print(html_output)
