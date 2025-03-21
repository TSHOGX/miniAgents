import sys
import os

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents import DbInfoAgent


agent = DbInfoAgent()

# Get a response to a user query
response = agent.run("How many tables are in the database and what are they used for?")
print(response)
