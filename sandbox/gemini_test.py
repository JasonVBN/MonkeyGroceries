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
- Recommend which stores have the requested products and also store all the products to buy.
- Output results as JSON: {
    "recommended_stores": {
        "store_name": [item1, item2, ...], ...
        }, 
        "all_products_to_buy":[]}
    }

"""
def min_store_cover(stores, items_to_buy):
    items_to_buy = set(items_to_buy)
    chosen_stores = []
    for i in stores:
        stores[i] = set(stores[i])
    while items_to_buy:
        # pick the store that covers the most uncovered items
        best_store = max(stores, key=lambda s: len(stores[s] & items_to_buy))
        chosen_stores.append(best_store)
        items_to_buy -= stores[best_store]

        # break if no progress
        if not stores[best_store]:
            break

    return chosen_stores
# Call the model
def ask_gemini(user_prompt, given_store):
    response = client.models.generate_content(
        model="gemini-2.5-pro",  # or "gemini-1.5-pro" for more reasoning
        contents=[
        {"role": "model", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "user", "parts": [{"text": user_prompt}]},],
        config={"response_mime_type": "application/json"}
    )
    import json
    stores = json.loads(response.text)
    with open('response.json', 'w') as f:   
        json.dump(stores, f, indent=2) 
    return stores


given_stores = {"Walmart", 'Target'
query = f"I need to buy milk, eggs, and chocolate."
response = ask_gemini(query)
stores_generated = response["recommended_stores"]
products = response["all_products_to_buy"]
print(min_store_cover(stores_generated, products))