# save as gemini_quickstart.py
import os
import sys
import json
from google import genai   # alias; see docs for exact import name
# if import fails, try: from google import genai OR import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Set GEMINI_API_KEY in your environment first.")
    sys.exit(1)

# Initialize the client
client = genai.Client(api_key=API_KEY)

for model in client.models.ListModels():
    print(model)
# Call the model
"""response = client.models.generate_content(
    model="gemini-1.5-pro",  # or "gemini-1.5-pro" for more reasoning
    contents="List 3 nearby stores where I can buy electronics."
)

print(response.text)"""