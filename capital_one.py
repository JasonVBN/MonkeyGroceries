import requests
import json
import os

# --- GLOBAL CONFIGURATION ---
# This is where your system attempts to load the API key
MY_NESSIE_KEY = os.getenv('CAPITALONE_KEY')
BASE_URL = "http://api.nessieisreal.com"

# =================================================================
# ⚙️ MERCHANT ID ASSIGNMENT FUNCTION (Embedded for Access)
# =================================================================

def assign_merchant_ids(stores_data: list, api_key: str) -> list:
    """
    Connects to the Nessie API to create a unique merchant for each store
    in the list and assigns the valid merchant_id to the store's dictionary.
    
    This function is now self-contained, using the imported 'requests' and 'json'.
    """
    if not api_key:
        print("\n🛑 Skipping Merchant ID assignment: API key is missing.")
        return stores_data
        
    print("--- Starting Nessie Merchant Setup (API Utility) ---")
    
    # Use the global BASE_URL defined above
    merchant_url = f'{BASE_URL}/merchants?key={api_key}' 
    
    for store in stores_data:
        store_name = store.get('name', 'Unknown Store')
        
        # Skip API call if ID is already assigned
        if store.get('merchant_id') is not None:
            print(f"✔️ {store_name} already has ID: {store['merchant_id'][:8]}...")
            continue
            
        payload = {
            "name": store_name,
            "category": ["food", "groceries", "retail"]
        }
        
        try:
            response = requests.post(
                merchant_url, 
                data=json.dumps(payload), 
                headers={'content-type': 'application/json'}
            )
            response.raise_for_status() # Raises an error for bad status codes
            
            new_merchant_id = response.json().get('_id')
            store['merchant_id'] = new_merchant_id
            
            print(f"➕ Created Merchant ID for {store_name}: {new_merchant_id[:8]}...")

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create Merchant for {store_name}. Error: {e}")
            store['merchant_id'] = None 
            
    return stores_data

# --- (The rest of your normalization and scoring functions go below this) ---
# --- (The calculate_final_weighted_score function can now call assign_merchant_ids directly) ---