from capital_one import assign_merchant_ids
import requests
import json
from dotenv import load_dotenv
load_dotenv()
import os
MY_NESSIE_KEY = os.getenv('CAPITALONE_KEY')

# -----------------------------
# NORMALIZATION + WEIGHTED SCORE FUNCTIONS
# -----------------------------

def assign_normalized_price_score(stores_data: list) -> list:
    if not stores_data:
        return stores_data

    try:
        prices = [store['estimated_price'] for store in stores_data]
    except KeyError:
        print("Error: Each store dictionary must contain the 'estimated_price' key.")
        return stores_data

    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price

    for store in stores_data:
        current_price = store['estimated_price']
        if price_range <= 0.01:
            normalized_score = 100.0
        else:
            normalized_score = 100.0 * (max_price - current_price) / price_range
        store['normalized_price_score'] = round(normalized_score, 2)

    return stores_data


def assign_normalized_time_score(stores_data: list) -> list:
    if not stores_data:
        return stores_data

    try:
        times = [store['travel_time_minutes'] for store in stores_data]
    except KeyError:
        print("Error: Each store dictionary must contain the 'travel_time_minutes' key.")
        return stores_data

    min_time = min(times)
    max_time = max(times)
    time_range = max_time - min_time

    for store in stores_data:
        current_time = store['travel_time_minutes']
        if time_range <= 0.01:
            normalized_score = 100.0
        else:
            normalized_score = 100.0 * (max_time - current_time) / time_range
        store['normalized_time_score'] = round(normalized_score, 2)

    return stores_data


def assign_normalized_rating_score(stores_data: list) -> list:
    if not stores_data:
        return stores_data

    try:
        ratings = [store['rating'] for store in stores_data]
    except KeyError:
        print("Error: Each store dictionary must contain the 'rating' key.")
        return stores_data

    MAX_RATING = 5.0
    min_rating = min(ratings)
    rating_range = MAX_RATING - min_rating

    for store in stores_data:
        current_rating = store['rating']
        if rating_range <= 0.01:
            normalized_score = 100.0
        else:
            normalized_score = 100.0 * (current_rating / MAX_RATING)
        store['normalized_rating_score'] = round(normalized_score, 2)

    return stores_data


# Assuming requests, json, os, MY_NESSIE_KEY, BASE_URL, and the assign_merchant_ids function
# are all defined in the same file above this code.

def calculate_final_weighted_score(stores_data: list, W_PRICE: float, W_TIME: float, W_RATING: float) -> list:
    """
    Calculates the final weighted score, ranks the stores, AND calls the 
    Merchant ID assignment function using the globally defined MY_NESSIE_KEY.
    """
    
    # --- 1. Scoring and Ranking Logic ---
    total_weight = W_PRICE + W_TIME + W_RATING
    if abs(total_weight - 1.0) > 0.01:
        print(f"Warning: Total weight ({total_weight:.2f}) does not sum to 1.0. Results will be scaled accordingly.")

    final_ranked_results = []
    
    # Calculate scores for all stores
    for store in stores_data:
        price_score = store.get('normalized_price_score', 0) * W_PRICE
        time_score = store.get('normalized_time_score', 0) * W_TIME
        rating_score = store.get('normalized_rating_score', 0) * W_RATING
        final_score = price_score + time_score + rating_score
        store['final_weighted_score'] = round(final_score, 2)
        final_ranked_results.append(store)

    # Rank the stores
    final_ranked_results.sort(key=lambda x: x['final_weighted_score'], reverse=True)

    # -------------------------------------------------------------
    # 2. API INTEGRATION: Assign the unique Nessie Merchant IDs 🌟
    # -------------------------------------------------------------
    
    # Access the global key variable defined at the top of the file
    global MY_NESSIE_KEY 
    MY_NESSIE_KEY = os.getenv('CAPITALONE_KEY')

    if MY_NESSIE_KEY is None:
        print("\n🛑 Skipping Merchant ID assignment: CAPITALONE_KEY environment variable is not set.")
        stores_with_ids = final_ranked_results
    else:
        # Call the helper function defined earlier in the file, passing the key
        stores_with_ids = assign_merchant_ids(final_ranked_results, MY_NESSIE_KEY)
    
    print("--- Final Ranking and Assignment Complete ---")
    return stores_with_ids


# -----------------------------
# TEST SECTION (runs when you do "python functions.py")
# -----------------------------
if __name__ == "__main__":
    # Example dataset to test all functions at once
    stores_data = [
        {"name": "Shop A", "estimated_price": 19.99, "travel_time_minutes": 12, "rating": 4.8},
        {"name": "Shop B", "estimated_price": 15.49, "travel_time_minutes": 18, "rating": 4.2},
        {"name": "Shop C", "estimated_price": 22.99, "travel_time_minutes": 10, "rating": 4.9},
        {"name": "Shop D", "estimated_price": 15.49, "travel_time_minutes": 15, "rating": 4.5},
        {"name": "Shop E", "estimated_price": 25.00, "travel_time_minutes": 25, "rating": 3.8},
    ]

    # Apply all normalization steps
    stores_data = assign_normalized_price_score(stores_data)
    print('after price score:', stores_data)
    stores_data = assign_normalized_time_score(stores_data)
    print('after time score:', stores_data)
    stores_data = assign_normalized_rating_score(stores_data)
    print('after rating score:', stores_data)
    
    # Compute weighted scores (example weights)
    ranked_results = calculate_final_weighted_score(
        stores_data,
        W_PRICE=0.4,
        W_TIME=0.3,
        W_RATING=0.3
    )

    # Print results
    print("\n=== Final Ranked Results ===")
    for rank, store in enumerate(ranked_results, start=1):
        print(store)
        # print(
        #     f"Rank {rank}: {store['name']}\n"
        #     f"  Price: ${store['estimated_price']}\n"
        #     f"  Time: {store['travel_time_minutes']} min\n"
        #     f"  Rating: {store['rating']}\n"
        #     f"  Price Score: {store['normalized_price_score']}\n"
        #     f"  Time Score: {store['normalized_time_score']}\n"
        #     f"  Rating Score: {store['normalized_rating_score']}\n"
        #     f"  Final Weighted Score: {store['final_weighted_score']}\n"
        # )



'''
previous working code:
def assign_normalized_price_score(stores_data: list) -> list:
    if not stores_data:
        return stores_data

    try:
        prices = [store['estimated_price'] for store in stores_data]
    except KeyError:
        print("Error: Each store dictionary must contain the 'estimated_price' key.")
        return stores_data

    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price

    for store in stores_data:
        current_price = store['estimated_price']
        if price_range <= 0.01:
            normalized_score = 100.0
        else:
            normalized_score = 100.0 * (max_price - current_price) / price_range
        store['normalized_price_score'] = round(normalized_score, 2)

    return stores_data


def assign_normalized_time_score(stores_data: list) -> list:
    if not stores_data:
        return stores_data

    try:
        times = [store['travel_time_minutes'] for store in stores_data]
    except KeyError:
        print("Error: Each store dictionary must contain the 'travel_time_minutes' key.")
        return stores_data

    min_time = min(times)
    max_time = max(times)
    time_range = max_time - min_time

    for store in stores_data:
        current_time = store['travel_time_minutes']
        if time_range <= 0.01:
            normalized_score = 100.0
        else:
            normalized_score = 100.0 * (max_time - current_time) / time_range
        store['normalized_time_score'] = round(normalized_score, 2)

    return stores_data


def assign_normalized_rating_score(stores_data: list) -> list:
    if not stores_data:
        return stores_data

    try:
        ratings = [store['rating'] for store in stores_data]
    except KeyError:
        print("Error: Each store dictionary must contain the 'rating' key.")
        return stores_data

    MAX_RATING = 5.0
    min_rating = min(ratings)
    rating_range = MAX_RATING - min_rating

    for store in stores_data:
        current_rating = store['rating']
        if rating_range <= 0.01:
            normalized_score = 100.0
        else:
            normalized_score = 100.0 * (current_rating / MAX_RATING)
        store['normalized_rating_score'] = round(normalized_score, 2)

    return stores_data


def calculate_final_weighted_score(stores_data: list, W_PRICE: float, W_TIME: float, W_RATING: float) -> list:
    total_weight = W_PRICE + W_TIME + W_RATING
    if abs(total_weight - 1.0) > 0.01:
        print(f"Warning: Total weight ({total_weight:.2f}) does not sum to 1.0. Results will be scaled accordingly.")

    final_ranked_results = []
    for store in stores_data:
        price_score = store.get('normalized_price_score', 0) * W_PRICE
        time_score = store.get('normalized_time_score', 0) * W_TIME
        rating_score = store.get('normalized_rating_score', 0) * W_RATING
        final_score = price_score + time_score + rating_score
        store['final_weighted_score'] = round(final_score, 2)
        final_ranked_results.append(store)

    final_ranked_results.sort(key=lambda x: x['final_weighted_score'], reverse=True)
    return final_ranked_results



'''