
from flask import Flask, jsonify, render_template, request
import requests
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/getlocs', methods=['GET','POST'])
def getlocs():
    r = float(request.args.get('radius'))
    print(f"[getlocs] radius: {r}")

    API_KEY = os.getenv('GMAPS_API_KEY')
    lat, lng = 30.2672, -97.7431
    radius = 1000*r  # meters
    type = 'store'

    url = (
        f'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        f'?location={lat},{lng}&radius={radius}&type={type}&key={API_KEY}'
    )

    print("calling places API...")
    response = requests.get(url)
    print("places API response received")
    results = response.json()['results']
    print(f"[getlocs] found {len(results)} places:")
    filtered = [{'name': x['name'], 'vicinity': x['vicinity']} for x in results]
    print(*filtered)
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