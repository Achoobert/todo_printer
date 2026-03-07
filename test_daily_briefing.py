import sys
import os

# Add the src directory to the Python path to allow importing daily_briefing_builder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from daily_briefing_builder import daily_briefing

# Test data
test_goals = "Test Goal One\nTest Goal Two\nTest Goal Three"

# Call the function
html_output = daily_briefing(test_goals)

# Print the output
print(html_output)
