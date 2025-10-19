
from flask import Flask, jsonify, render_template, request
import requests
import time
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def fetch_all_pages(lat, lng, radius, place_type, api_key):
    """Fetch all pages (up to 60 results) for a single location"""
    url = (
        f'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        f'?location={lat},{lng}&radius={radius}&type={place_type}&key={api_key}'
    )
    
    results = []
    next_page_token = None
    
    print(f"  Fetching page 1 at ({lat},{lng})...")
    response = requests.get(url)
    data = response.json()
    results.extend(data.get('results', []))
    next_page_token = data.get('next_page_token')
    
    # page = 2
    # while next_page_token:
        # time.sleep(2)  # Required delay
        # print(f"  Fetching page {page}...")
        # next_url = (
        #     f'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        #     f'?pagetoken={next_page_token}&key={api_key}'
        # )
        # response = requests.get(next_url)
        # data = response.json()
        # results.extend(data.get('results', []))
        # next_page_token = data.get('next_page_token')
        # page += 1
    
    print(f"  Got {len(results)} results from this location")
    return results

@app.route('/getlocs', methods=['GET','POST'])
def getlocs():
    r = float(request.args.get('radius'))
    print(f"[getlocs] radius: {r} km")

    API_KEY = os.getenv('GMAPS_API_KEY')
    center_lat, center_lng = 30.2672, -97.7431
    
    all_results = []
    seen_place_ids = set()
    
    # 1. Main search at center
    print("Searching at center point...")
    results = fetch_all_pages(center_lat, center_lng, int(1000*r), 'store', API_KEY)
    for place in results:
        place_id = place.get('place_id')
        if place_id not in seen_place_ids:
            seen_place_ids.add(place_id)
            all_results.append(place)
    
    # 2. Search at 4 cardinal points (N, S, E, W)
    offset = r * 0.6  # 60% of radius
    offsets = [
        (offset/111, 0, "North"),              # North
        (-offset/111, 0, "South"),             # South
        (0, offset/(111*0.87), "East"),        # East (adjusted for Austin latitude)
        (0, -offset/(111*0.87), "West")        # West
    ]
    
    for lat_off, lng_off, direction in offsets:
        print(f"Searching {direction} offset point...")
        search_lat = center_lat + lat_off
        search_lng = center_lng + lng_off
        results = fetch_all_pages(search_lat, search_lng, int(1000*r*0.7), 'store', API_KEY)
        
        for place in results:
            place_id = place.get('place_id')
            if place_id not in seen_place_ids:
                seen_place_ids.add(place_id)
                all_results.append(place)
    
    print(f"[getlocs] found {len(all_results)} unique places total")
    filtered = [{'name': x['name'], 'vicinity': x['vicinity']} for x in all_results]
    
    return jsonify({'locations': filtered})

# @app.route('/audio', methods=['POST'])
# def receive_audio():
#     data = request.get_json()
#     audio_data = data.get('audio')
#     # Here you can process the audio_data as needed
#     return jsonify({'status': 'Audio received successfully'})

if __name__ == '__main__':
    app.run(port=5000, 
            debug=True
    )