"""
Example script showing how to load environment variables from .env file
for use with EODAG.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the environment variables
username = os.environ.get("EODAG__COP_DATASPACE__AUTH__CREDENTIALS__USERNAME")
password = os.environ.get("EODAG__COP_DATASPACE__AUTH__CREDENTIALS__PASSWORD")

print(f"Username loaded: {username is not None}")
print(f"Password loaded: {password is not None}")

# Example of how to use these with EODAG
# from eodag import EODataAccessGateway
# dag = EODataAccessGateway()
# dag.set_preferred_provider("cop_dataspace")
