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
"""'''
for model in client.models.list():
    print(model)"""
SYSTEM_PROMPT = """
You are ShopSmartAI — a shopping optimization assistant.
Your job:
- Take a list of products and nearby store catalogs.
- Recommend which stores have the requested products.
- Output results as JSON: {"recommended_stores": ["..."]}
"""

# Call the model
def ask_gemini(user_prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # or "gemini-1.5-pro" for more reasoning
        contents=[
        {"role": "system", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "user", "parts": [{"text": user_prompt}]}
    ]
products = ["milk", "bread"]
stores = {"Walmart": ["milk", "eggs"], "Target": ["chips", "bread"]}
query = f"Products to find: {products}. Store data: {stores}."
response = ask_gemini(query)
print(response.text)