// ============================================================
// ISCS Web Dashboard - Main Application
// Connects to FastAPI backend and displays live traffic data
// ============================================================

const CONFIG = {
    API_BASE_URL: 'http://192.168.1.21:8000',
    CENTER_LAT: 31.9454,
    CENTER_LNG: 35.9284,
    ZOOM_LEVEL: 14,
    REFRESH_INTERVAL: 5000, // 5 seconds
};

// Global state
let map;
let rsuMarkers = {};
let edgePolylines = [];
let selectedSegment = null;
let selectedRsu = null;
let segmentsData = [];

// ============================================================
// MAP INITIALIZATION
// ============================================================

function initMap() {
    map = L.map('map').setView(
        [CONFIG.CENTER_LAT, CONFIG.CENTER_LNG],
        CONFIG.ZOOM_LEVEL
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        opacity: 0.9,
    }).addTo(map);
}

// ============================================================
// STATUS COLOR & EMOJI HELPERS
// ============================================================

function getStatusColor(status) {
    const colors = {
        free: '#10b981',
        moderate: '#f59e0b',
        congested: '#ef6737',
        severe: '#dc2626',
    };
    return colors[status] || '#6b7280';
}

function getStatusEmoji(status) {
    
    return'';
}

// ============================================================
// MARKER & POLYLINE MANAGEMENT
// ============================================================

function clearMapElements() {
    // Clear RSU markers
    Object.values(rsuMarkers).forEach(({ marker }) => {
        if (marker) marker.remove();
    });
    rsuMarkers = {};

    // Clear edge polylines
    edgePolylines.forEach(poly => {
        if (poly) poly.remove();
    });
    edgePolylines = [];
}

function addEdgePolyline(path, status) {
    if (!path || path.length === 0) return;

    const latLngs = path.map(p => [p.lat, p.lng]);
    const color = getStatusColor(status);

    const polyline = L.polyline(latLngs, {
        color: color,
        weight: 6,
        opacity: 0.7,
        lineCap: 'round',
        lineJoin: 'round',
    }).addTo(map);

    edgePolylines.push(polyline);
}

function addRsuMarker(rsu, segment) {
    const color = getStatusColor(rsu.status);
    

    const iconHtml = `
        <div style="
            background-color: ${color};
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 22px;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        ">
            RSU
        </div>
    `;

    const icon = L.divIcon({
        html: iconHtml,
        iconSize: [44, 44],
        className: 'custom-marker',
    });

    const marker = L.marker([rsu.lat, rsu.lng], { icon }).addTo(map);

    const popupContent = `
        <div class="popup-header">${rsu.rsu_id}</div>
        <div class="popup-item">
            <span class="popup-label">Segment:</span>
            <span class="popup-value">${segment}</span>
        </div>
        <div class="popup-item">
            <span class="popup-label">Speed:</span>
            <span class="popup-value">${(rsu.avg_speed || 0).toFixed(1)} km/h</span>
        </div>
        <div class="popup-item">
            <span class="popup-label">Status:</span>
            <span class="popup-value">${rsu.status.toUpperCase()}</span>
        </div>
    `;

    marker.bindPopup(popupContent);

    marker.on('click', () => {
        showRsuDetails(rsu, segment);
    });

    rsuMarkers[rsu.rsu_id] = { marker, rsu, segment };
}

// ============================================================
// DATA DISPLAY FUNCTIONS
// ============================================================

function displaySegments(segments) {
    const segmentsList = document.getElementById('segments-list');
    segmentsList.innerHTML = '';

    if (!segments || segments.length === 0) {
        segmentsList.innerHTML = '<p class="no-data">No segments available</p>';
        return;
    }

    segments.forEach(segment => {
        const avgSpeed = segment.rsus.length > 0
            ? (segment.rsus.reduce((sum, r) => sum + (r.avg_speed || 0), 0) / segment.rsus.length).toFixed(1)
            : 0;

        const status = determineStatus(avgSpeed);

        const item = document.createElement('div');
        item.className = `segment-item ${selectedSegment === segment.segment ? 'active' : ''}`;
        item.innerHTML = `
            <div class="item-header">
                <span class="item-name">${segment.segment}</span>
                <span class="item-status status-${status}">${status}</span>
            </div>
            <div class="item-info">
                <div>Speed: ${avgSpeed} km/h</div>
                <div>RSUs: ${segment.rsus.length}</div>
                <div>Edges: ${segment.edges.length}</div>
            </div>
        `;

        item.addEventListener('click', () => showSegmentDetails(segment));
        segmentsList.appendChild(item);
    });
}

function displayRsus(rsus, segment) {
    const rsuList = document.getElementById('rsu-list');
    rsuList.innerHTML = '';

    if (!rsus || rsus.length === 0) {
        rsuList.innerHTML = '<p class="no-data">No RSUs in this segment</p>';
        return;
    }

    rsus.forEach(rsu => {
        const item = document.createElement('div');
        item.className = `rsu-item ${selectedRsu === rsu.rsu_id ? 'active' : ''}`;
        item.innerHTML = `
            <div class="item-header">
                <span class="item-name">${rsu.rsu_id}</span>
                <span class="item-status status-${rsu.status}"> ${rsu.status.toUpperCase()}</span>
            </div>
            <div class="item-info">
                <div>Speed: ${(rsu.avg_speed || 0).toFixed(1)} km/h</div>
                <div>Position: ${rsu.lat.toFixed(4)}, ${rsu.lng.toFixed(4)}</div>
            </div>
        `;

        item.addEventListener('click', () => showRsuDetails(rsu, segment));
        rsuList.appendChild(item);
    });
}

// ============================================================
// DETAIL VIEWS
// ============================================================

function showSegmentDetails(segment) {
    selectedSegment = segment.segment;
    selectedRsu = null;

    const detailsContent = document.getElementById('details-content');

    const rsusInfo = segment.rsus.map(r => 
        `<div>${r.rsu_id}: ${(r.avg_speed || 0).toFixed(1)} km/h (${r.status})</div>`
    ).join('');

    const edgesInfo = segment.edges.map((e, i) => 
        `<div>Edge ${i + 1}: ${(e.avg_speed || 0).toFixed(1)} km/h (${e.status})</div>`
    ).join('');

    detailsContent.innerHTML = `
        <div class="details-item">
            <div class="detail-label">Segment</div>
            <div class="detail-value"><strong>${segment.segment}</strong></div>
        </div>

        <div class="details-item">
            <div class="detail-label">RSU Count</div>
            <div class="detail-value"><strong>${segment.rsus.length}</strong></div>
        </div>

        <div class="details-item">
            <div class="detail-label">Edge Count</div>
            <div class="detail-value"><strong>${segment.edges.length}</strong></div>
        </div>

        <div class="details-item">
            <div class="detail-label">RSUs Status</div>
            <div class="detail-value">
                <div class="edge-info">${rsusInfo}</div>
            </div>
        </div>

        ${segment.edges.length > 0 ? `
        <div class="details-item">
            <div class="detail-label">Edges Status</div>
            <div class="detail-value">
                <div class="edge-info">${edgesInfo}</div>
            </div>
        </div>
        ` : ''}
    `;

    displayRsus(segment.rsus, segment.segment);
}

function showRsuDetails(rsu, segment) {
    selectedRsu = rsu.rsu_id;
    selectedSegment = segment;

    const detailsContent = document.getElementById('details-content');
    const healthPercentage = Math.min(100, ((rsu.avg_speed || 0) / 70) * 100);

    detailsContent.innerHTML = `
        <div class="details-item">
            <div class="detail-label">RSU ID</div>
            <div class="detail-value"><strong>${rsu.rsu_id}</strong></div>
        </div>

        <div class="details-item">
            <div class="detail-label">Segment</div>
            <div class="detail-value"><strong>${segment}</strong></div>
        </div>

        <div class="details-item">
            <div class="detail-label">Status</div>
            <div class="detail-value">
                <strong>${rsu.status.toUpperCase()}</strong>
            </div>
        </div>

        <div class="details-item">
            <div class="detail-label">Average Speed</div>
            <div class="detail-value">
                <strong>${(rsu.avg_speed || 0).toFixed(1)} km/h</strong>
                <div class="health-bar">
                    <div class="health-fill" style="width: ${healthPercentage}%"></div>
                </div>
                <small>${getSpeedDescription(rsu.avg_speed)}</small>
            </div>
        </div>

        <div class="details-item">
            <div class="detail-label">Position</div>
            <div class="detail-value">
                Lat: ${rsu.lat.toFixed(6)}<br>
                Lng: ${rsu.lng.toFixed(6)}
            </div>
        </div>

        <div class="details-item">
            <div class="detail-label">Last Updated</div>
            <div class="detail-value">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
}

// ============================================================
// HELPER FUNCTIONS
// ============================================================

function determineStatus(speed) {
    if (speed >= 60) return 'free';
    if (speed >= 40) return 'moderate';
    if (speed >= 20) return 'congested';
    return 'severe';
}

function getSpeedDescription(speed) {
    if (speed >= 60) return ' Free flow traffic';
    if (speed >= 40) return ' Moderate traffic';
    if (speed >= 20) return ' Congested traffic';
    return ' Severe congestion';
}

function updateServerStatus(online) {
    const indicator = document.getElementById('server-status');
    indicator.classList.toggle('online', online);
    indicator.textContent = online ? '● Online' : '● Offline';
}

function updateLastUpdate() {
    const now = new Date();
    document.getElementById('last-update').textContent = 
        `Last update: ${now.toLocaleTimeString()}`;
}

// ============================================================
// DATA FETCHING
// ============================================================

async function fetchStateData() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/state`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success && data.segments) {
            segmentsData = data.segments;
            updateMapAndUI(data.segments);
            updateServerStatus(true);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        updateServerStatus(false);
    } finally {
        updateLastUpdate();
    }
}

function updateMapAndUI(segments) {
    clearMapElements();

    segments.forEach(segment => {
        // Add edges (polylines)
        segment.edges.forEach(edge => {
            addEdgePolyline(edge.path, edge.status);
        });

        // Add RSU markers
        segment.rsus.forEach(rsu => {
            addRsuMarker(rsu, segment.segment);
        });
    });

    displaySegments(segments);

    // Show first segment by default
    if (segments.length > 0) {
        showSegmentDetails(segments[0]);
    }
}

// ============================================================
// INITIALIZATION
// ============================================================

window.addEventListener('load', () => {
    console.log(' Intelligent Street Dashboard initializing...');
    
    initMap();
    fetchStateData();

    // Refresh data every 5 seconds
    setInterval(fetchStateData, CONFIG.REFRESH_INTERVAL);

    console.log(' Dashboard ready');
});

// ============================================================
// ERROR HANDLING
// ============================================================

window.addEventListener('error', (e) => {
    console.error('Unexpected error:', e.error);
});
