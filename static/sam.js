let map;
let originPlace = null;
let markers = [];
let infoWindow;

const MILES_TO_METERS = 1609.34;

async function initMap() {
    const { Map, InfoWindow } = await google.maps.importLibrary("maps");
    const placeAutocomplete = document.querySelector('gmp-basic-place-autocomplete');

    map = new Map(document.getElementById("map"), {
        center: { lat: 37.0902, lng: -95.7129 },
        zoom: 4,
        mapId: "DEMO_MAP_ID",
        gestureHandling: "greedy",
    });

    infoWindow = new InfoWindow();

    placeAutocomplete.addEventListener('gmp-select', async (event) => {
        originPlace = event.place;
    });

    document.getElementById('radius-slider').addEventListener('input', (e) => {
        document.getElementById('radius-value').textContent = e.target.value;
    });

    document.getElementById('find-stores-btn').addEventListener('click', findNearbyStores);
}

async function findNearbyStores() {
    if (!originPlace) {
        document.getElementById('status-message').textContent = 'Please select a starting address.';
        return;
    }

    await originPlace.fetchFields({ fields: ['location'] });
    if (!originPlace.location) {
        document.getElementById('status-message').textContent = 'Could not find location for the selected address.';
        return;
    }

    clearResults();
    document.getElementById('status-message').textContent = 'Searching for grocery stores...';

    const { Place } = await google.maps.importLibrary("places");
    const radiusInMeters = document.getElementById('radius-slider').value * MILES_TO_METERS;

    const request = {
        locationRestriction: {
            center: originPlace.location,
            radius: radiusInMeters,
        },
        includedPrimaryTypes: ['grocery_store', 'supermarket'],
        maxResultCount: 10, // Keep the number of destinations reasonable for the matrix
    };

    try {
        const { places } = await Place.searchNearby(request);

        if (places.length === 0) {
            document.getElementById('status-message').textContent = 'No grocery stores found within the selected radius.';
            return;
        }

        document.getElementById('status-message').textContent = 'Calculating travel times...';
        await getDistances(places);

    } catch (error) {
        console.error('Nearby search failed:', error);
        document.getElementById('status-message').textContent = 'Error finding stores. Please try again.';
    }
}

async function getDistances(places) {
    const travelMode = document.getElementById('travel-mode-select').value;
    const destinations = await Promise.all(places.map(async (place) => {
        await place.fetchFields({ fields: ['location'] });
        return { waypoint: { location: place.location } };
    }));

    const matrixRequest = {
        origins: [{ waypoint: { location: originPlace.location } }],
        destinations: destinations,
        travelMode: travelMode,
    };

    try {
        const response = await fetch("https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": "YOUR_API_KEY",
                "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status"
            },
            body: JSON.stringify(matrixRequest)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const matrixData = await response.json();
        displayResults(places, matrixData);

    } catch (error) {
        console.error("Route Matrix request failed:", error);
        document.getElementById('status-message').textContent = 'Could not calculate travel times.';
        // Display results without travel times as a fallback
        displayResults(places, []);
    }
}

async function displayResults(places, matrixData) {
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    clearResults();
    const resultsList = document.getElementById('results-list');
    const bounds = new google.maps.LatLngBounds();

    await Promise.all(places.map(async (place, i) => {
        await place.fetchFields({ fields: ['displayName', 'formattedAddress', 'location'] });

        const matrixResult = matrixData.find(res => res.destinationIndex === i);
        
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.innerHTML = `
            <h3>${place.displayName}</h3>
            <p>${place.formattedAddress}</p>
            ${matrixResult && matrixResult.status.code === 0 ? 
                `<p><strong>${Math.round(matrixResult.duration.slice(0, -1) / 60)} mins</strong> (${(matrixResult.distanceMeters / MILES_TO_METERS).toFixed(1)} mi)</p>` : 
                '<p>Travel time not available.</p>'}
        `;

        const marker = new AdvancedMarkerElement({
            map,
            position: place.location,
            title: place.displayName,
        });

        marker.addListener('click', () => {
            highlightResult(resultItem, true);
            infoWindow.setContent(`
                <div class="info-window-content">
                    <h3>${place.displayName}</h3>
                    <p>${place.formattedAddress}</p>
                </div>
            `);
            infoWindow.open(map, marker);
        });

        resultItem.addEventListener('click', () => {
            map.panTo(place.location);
            map.setZoom(15);
            marker.gmpClickable = true;
            google.maps.event.trigger(marker, 'click');
        });

        markers.push(marker);
        resultsList.appendChild(resultItem);
        bounds.extend(place.location);
    }));

    if (originPlace && originPlace.location) {
        bounds.extend(originPlace.location);
    }
    map.fitBounds(bounds);
}

function highlightResult(resultItem, scroll) {
    document.querySelectorAll('.result-item').forEach(item => item.classList.remove('active'));
    if (resultItem) {
        resultItem.classList.add('active');
        if (scroll) {
            resultItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}

function clearResults() {
    document.getElementById('results-list').innerHTML = '';
    document.getElementById('status-message').textContent = '';
    markers.forEach(marker => marker.map = null);
    markers = [];
    infoWindow.close();
}

initMap();