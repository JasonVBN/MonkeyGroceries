# save as gemini_quickstart.py
import os
import sys
import json
from google import genai   # alias; see docs for exact import name
# if import fails, try: from google import genai OR import google.generativeai as genai
# import google.generativeai as genai
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
- Given 
- Recommend which stores have the requested products. Store each store name as a key, and the list of products it has as the value.
- Output results as JSON: 
{
    "recommended_stores": {
        "store_1": [item1, item2, ...], 
        "store_2": [item3, item4, ...],
        ...
    }, 
}

"""
# Call the model
given_stores = ["Walmart", 'Best Buy', 'Target', 'Costco'] # Store list given by jason
def ask_gemini(user_prompt, given_store=given_stores):
    print("[ask_gemini] user_prompt:", user_prompt)
    response = client.models.generate_content(
        model="gemini-2.5-pro",  # or "gemini-1.5-pro" for more reasoning
        contents=[
        {"role": "model", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "user", "parts": [{"text": user_prompt+f'Here are the stores you can choose from: {given_store}'}]},],
        config={"response_mime_type": "application/json"}
    )
    stores = json.loads(response.text)
    with open('response.json', 'w') as f:   
        json.dump(stores, f, indent=2) 
    return stores

if __name__ == "__main__":
    query = f"I need chocolate" # Example user prompt
    response = ask_gemini(query)
    stores_generated = response["recommended_stores"]
    print(stores_generated)