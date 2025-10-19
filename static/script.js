let map, infoWindow;
let markers = [];
let currentUserLocation;

async function initMap() {
  const { Map, InfoWindow } = await google.maps.importLibrary("maps");
  
  map = new Map(document.getElementById("map"), {
    center: { lat: 40.73061, lng: -73.935242 }, // Default to NYC
    zoom: 12,
    mapId: 'DEMO_MAP_ID',
    gestureHandling: 'greedy'
  });

  infoWindow = new InfoWindow();

  // Get user's current location
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        currentUserLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        map.setCenter(currentUserLocation);

        const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

        // Create a custom DOM element for the marker to replicate the blue dot
        const userMarkerEl = document.createElement('div');
        userMarkerEl.style.width = '14px';
        userMarkerEl.style.height = '14px';
        userMarkerEl.style.borderRadius = '50%';
        userMarkerEl.style.backgroundColor = '#4285F4';
        userMarkerEl.style.border = '2px solid white';
        userMarkerEl.style.boxShadow = '0 2px 4px rgba(0,0,0,0.4)';

        new AdvancedMarkerElement({
            position: currentUserLocation,
            map: map,
            title: "Your Location",
            content: userMarkerEl
        });

        document.getElementById('status-message').textContent = 'Location found. Enter radius and search.';
      },
      () => {
        handleLocationError(true);
      }
    );
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false);
  }

  document.getElementById('search-button').addEventListener('click', handleSearch);
}

function handleLocationError(browserHasGeolocation) {
  const statusMessage = document.getElementById('status-message');
  statusMessage.textContent = browserHasGeolocation
    ? "Error: The Geolocation service failed."
    : "Error: Your browser doesn't support geolocation.";
}

async function handleSearch() {
    if (!currentUserLocation) {
        document.getElementById('status-message').textContent = 'Error: Could not determine your location.';
        return;
    }

    clearResults();
    document.getElementById('status-message').textContent = 'Searching for nearby grocery stores...';

    const radiusInMiles = document.getElementById('radius-input').value;
    const radiusInMeters = radiusInMiles * 1609.34;

    const { Place } = await google.maps.importLibrary("places");

    const request = {
        location: currentUserLocation,
        radius: radiusInMeters,
        type: 'grocery_or_supermarket',
        fields: ['displayName', 'location', 'formattedAddress', 'place_id', 'priceLevel']
    };

    try {
        const { places } = await Place.searchNearby(request);

        if (places.length === 0) {
            document.getElementById('status-message').textContent = 'No grocery stores found within the specified radius.';
            return;
        }

        document.getElementById('status-message').textContent = 'Calculating travel times...';
        calculateRoutes(places);

    } catch (error) {
        console.error('Place search failed:', error);
        document.getElementById('status-message').textContent = 'Error: Failed to search for places.';
    }
}

async function calculateRoutes(places) {
    const destinations = places.map(place => ({ waypoint: { placeId: place.place_id } }));
    const origins = [{ waypoint: { location: { latLng: currentUserLocation } } }];

    const request = {
        origins: origins,
        destinations: destinations,
        travelMode: 'DRIVE',
    };

    try {
        const response = await fetch("https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": "YOUR_API_KEY",
                "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status"
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const routeData = await response.json();
        displayResults(places, routeData);

    } catch (error) {
        console.error("Route Matrix request failed:", error);
        document.getElementById('status-message').textContent = 'Error: Could not calculate travel times. Displaying stores without route data.';
        displayResults(places, null); // Display results even if routing fails
    }
}

async function displayResults(places, routeData) {
    const resultsList = document.getElementById('results-list');
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    const bounds = new google.maps.LatLngBounds();

    places.forEach((place, i) => {
        const routeInfo = routeData ? routeData.find(r => r.destinationIndex === i) : null;

        // Create Marker
        const marker = new AdvancedMarkerElement({
            map: map,
            position: place.location,
            title: place.displayName,
        });

        markers.push(marker);
        bounds.extend(place.location);

        // Create List Item
        const li = document.createElement('li');
        let price = place.priceLevel ? '$'.repeat(place.priceLevel) : 'N/A';
        let durationText = 'N/A';
        let distanceText = 'N/A';

        if (routeInfo && routeInfo.status.code === 0) { // 0 is 'OK'
            const durationSeconds = parseInt(routeInfo.duration.slice(0, -1));
            durationText = `${Math.round(durationSeconds / 60)} min`;
            distanceText = `${(routeInfo.distanceMeters / 1609.34).toFixed(1)} mi`;
        }

        li.innerHTML = `
            <h3>${place.displayName}</h3>
            <p>${place.formattedAddress}</p>
            <p>Price: <span class="price-level">${price}</span></p>
            <p>Drive: ${durationText}, ${distanceText}</p>
        `;

        li.addEventListener('click', () => {
            map.panTo(place.location);
            map.setZoom(15);
            infoWindow.setContent(`<h3>${place.displayName}</h3><p>${place.formattedAddress}</p>`);
            infoWindow.open(map, marker);
        });

        marker.addListener('click', () => {
            li.click();
        });

        resultsList.appendChild(li);
    });

    if (places.length > 0) {
        bounds.extend(currentUserLocation);
        map.fitBounds(bounds);
        document.getElementById('status-message').textContent = `Found ${places.length} stores.`;
    }
}

function clearResults() {
    markers.forEach(marker => marker.map = null);
    markers = [];
    document.getElementById('results-list').innerHTML = '';
}

initMap();