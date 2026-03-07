import sys
import os

# Add the src directory to the Python path to allow importing daily_briefing_builder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from short_task import create_short_task_html

# Test data
# test_goals = "Test item Onethatgoes onand on and on and on and on and on and on and on\nTest item Two"
test_goals = "Test item one\n two\n three"
# Call the function
html_output = create_short_task_html(test_goals)

# Print the output
print(html_output)
