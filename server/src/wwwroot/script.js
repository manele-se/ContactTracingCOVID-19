// Initial values for the Map instance
const CENTER_LAT = 57.7069;
const CENTER_LNG = 11.9376;
const INITIAL_ZOOM = 19;
const MAP_TYPE = 'satellite';

const HOSPITAL_LAT = 57.706976;
const HOSPITAL_LNG = 11.937991;
const HOSPITAL_RADIUS = 25;
const circleStyle = {
  strokeColor: '#112299',
  strokeOpacity: 0.8,
  strokeWeight: 2.0,
  fillColor: '#5599ff',
  fillOpacity: 0.2
};
const hospitalStyle = {
  strokeColor: '#ff0000',
  strokeOpacity: 0.8,
  strokeWeight: 2.0,
  fillColor: '#ff0000',
  fillOpacity: 0.2
};

// Store all devices by their name
const devices = {};

let ws;
let map;

/**
   * Returns a device marker. If the name is already known, returns an existing marker. Otherwise creates a new.
   */
function getOrCreateDeviceMarker(name) {
  if (name in devices) {
    // This is a known device
    return devices[name];
  } else {
    // The name is on the format "device-N". Get the "N" part and use it as a label.
    const label = name.substr(0, 1);
    let link = 'http://maps.google.com/mapfiles/kml/paddle/grn-blank.png';

    if (name.startsWith('Mallory')) {
      link = 'http://maps.google.com/mapfiles/kml/paddle/purple-blank.png';
    }
    // Create a new marker on the map
    const newDevice = new google.maps.Marker({
      position: new google.maps.LatLng(CENTER_LAT, CENTER_LNG),
      title: name,
      label: label,
      draggable: true,
      clickable: true,
      icon: {
        url: link
      }
    });

    newDevice.setMap(map);
    newDevice.addListener('click', () => {
      const message = {
        action: 'toggle',
        name: name
      };
      ws.send(JSON.stringify(message));
    });
    newDevice.addListener('dragstart', (evt) => {
      newDevice.dragging = true;
      const message = {
        action: 'stop',
        name: name
      };
      ws.send(JSON.stringify(message));
    });
    newDevice.addListener('dragend', (evt) => {
      const newLat = evt.latLng.lat();
      const newLng = evt.latLng.lng();
      newDevice.dragging = false;
      const message = {
        action: 'move',
        name: name,
        lat: newLat,
        lng: newLng
      };
      ws.send(JSON.stringify(message));
    });

    // Add the device
    devices[name] = newDevice;

    return newDevice;
  }
}

/**
   * Create a circle on the map that grows to 10 meters in radius
   */
function showBroadcastCircle(lat, lng) {
  // Create a small circle
  const circle = new google.maps.Circle({
    center: new google.maps.LatLng(lat, lng),
    map: map,
    radius: 0.5,
    ...circleStyle
  });

  // Let the circle grow over time
  for (let r = 1; r <= 10; r += 0.5) {
    window.setTimeout(() => {
      circle.setRadius(r);
    }, r * 95);
  }

  // Remove the circle when it's done
  window.setTimeout(() => circle.setMap(null), 1000);
}

/**
   * Connect to the WebSocket endpoint and start communicating
   */
function connectToWebSocket() {
  // Get the WecSocket URL
  const wsAddress = `ws://${document.location.host}/ws`;
  ws = new WebSocket(wsAddress);

  // Connection was established.
  ws.onopen = (evt) => {
    console.log('WebSocket connection established.');
  };

  // Connection was closed or broken. Retry connection after a second.
  ws.onclose = (evt) => {
    console.warn('Closed WebSocket connection. Retrying...');
    window.setTimeout(() => connectToWebSocket(), 1000);
  };

  // Incoming message from the server
  ws.onmessage = (evt) => {
    // Parse the message
    const { name, lat, lng, bearing, action, trail } = JSON.parse(evt.data);

    // Check if the device is known
    const device = name && getOrCreateDeviceMarker(name);

    switch (action) {
      case 'move':
        // Move the marker to the device's new position
        if (device.dragging) return;
        device.setPosition(new google.maps.LatLng(lat, lng));
        break;

      case 'remove':
        // Remove the marker
        device.setMap(null);
        break;

      case 'broadcast':
        // Show a circle on the map that grows over time from 1 meter radius to 10 meter radius
        device.setPosition(new google.maps.LatLng(lat, lng));
        showBroadcastCircle(lat, lng);
        break;

      case 'location_trail':
        //show the trail of infected
        const coordinates = trail.map(([ lat, lng ]) => ({
          lat: lat,
          lng: lng
        }));
        const polyline = new google.maps.Polyline({
          path: coordinates,
          strokeColor: 'red',
          strokeWeight: 10
        });
        polyline.setMap(map);
        break;

      case 'change_color_red':
        //change color to red to the sick marker
        setTimeout(() => device.setIcon('http://maps.google.com/mapfiles/kml/paddle/red-blank.png'), 2000);
        break;

      case 'change_color_yellow':
        device.setIcon('http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png');
        break;

      case 'change_color_green':
        //change color to red to the sick marker
        device.setIcon('http://maps.google.com/mapfiles/kml/paddle/grn-blank.png');
        break;

      case 'change_color_purple':
        //change color to red to the sick marker
        device.setIcon('http://maps.google.com/mapfiles/kml/paddle/purple-blank.png');
        break;

      case 'receive':
        break;
    }
  };
}

/**
   * This function gets called when the Google Maps API has been loaded
   */
function initMap() {
  // Find the <div id="map"> element
  const mapElement = document.getElementById('map');

  // Create a Map instance showing the selected region
  map = new google.maps.Map(mapElement, {
    center: {
      lat: CENTER_LAT,
      lng: CENTER_LNG
    },
    zoom: INITIAL_ZOOM,
    mapTypeId: MAP_TYPE,
    disableDefaultUI: true
  });

  hospital = new google.maps.Circle({
    center: new google.maps.LatLng(HOSPITAL_LAT, HOSPITAL_LNG),
    radius: HOSPITAL_RADIUS,
    map: map,
    ...hospitalStyle
  });

  connectToWebSocket(map);

  return map;
}
