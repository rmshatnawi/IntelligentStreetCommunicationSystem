# ISCS Web Dashboard

## Overview

A real-time traffic monitoring dashboard for the **Intelligent Street Communication System (ISCS)**. This web application displays:

- **Interactive Map** with color-coded road segments and RSU locations
- **Segment Overview** showing traffic status across all monitored roads
- **RSU Details** including speed, position, and health metrics
- **Live Updates** refreshing every 5 seconds

## Features

### 🗺️ Interactive Map
- Built with Leaflet.js and OpenStreetMap
- Color-coded polylines representing road segments:
  - 🟢 Green: Free traffic (≥60 km/h)
  - 🟡 Yellow: Moderate (40-59 km/h)
  - 🟠 Orange: Congested (20-39 km/h)
  - 🔴 Red: Severe (<20 km/h)
- Clickable RSU markers with detailed popups
- Auto-centers on Amman, Jordan

### 📊 Segment Panel
- Lists all monitored road segments
- Shows average speed and status for each segment
- Click to view detailed segment information

### 📍 RSU Panel
- Lists all Roadside Units in selected segment
- Displays current speed and coordinates
- Click to view RSU-specific health metrics

### 📋 Details Panel
- **For Segments**: RSU count, edge count, per-RSU status breakdown
- **For RSUs**: Speed analysis with health bar, position, status interpretation

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- ISCS backend server running on `http://localhost:8000`

### Installation

1. Place the dashboard files in your project:
```bash
# Copy to your project directory
cp -r web_dashboard/ /path/to/project/
```

2. Open in browser:
```bash
# Navigate to the directory
cd web_dashboard

# Open index.html
# On macOS: open index.html
# On Windows: start index.html
# Or simply double-click the file
```

### Configuration

Edit `app.js` to change the backend URL or map center:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',  // Your backend server
    CENTER_LAT: 31.9454,                     // Map center latitude
    CENTER_LNG: 35.9284,                     // Map center longitude (Amman)
    ZOOM_LEVEL: 14,                          // Initial zoom
    REFRESH_INTERVAL: 5000,                  // Update interval (ms)
};
```

## Backend Integration

### API Endpoints Used

The dashboard connects to your FastAPI backend using the `/state` endpoint:

```
GET /state
```

**Response Format:**
```json
{
  "success": true,
  "segments": [
    {
      "segment": "Petra St",
      "rsus": [
        {
          "rsu_id": "RSU_01",
          "lat": 31.9460,
          "lng": 35.9270,
          "avg_speed": 42.0,
          "status": "moderate"
        }
      ],
      "edges": [
        {
          "status": "moderate",
          "avg_speed": 45.0,
          "path": [
            {"lat": 31.9460, "lng": 35.9270},
            {"lat": 31.9470, "lng": 35.9280}
          ]
        }
      ]
    }
  ]
}
```

### CORS Configuration

Ensure your FastAPI backend allows requests from the dashboard:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## File Structure

```
web_dashboard/
├── index.html        # Main HTML file
├── styles.css        # Styling and layout
├── app.js            # JavaScript logic
└── README.md         # This file
```

## Technology Stack

- **Leaflet.js** - Interactive mapping
- **OpenStreetMap** - Map tiles
- **CSS3** - Modern styling with gradients and animations
- **Vanilla JavaScript** - No external dependencies

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Auto-updates every 5 seconds (configurable)
- Efficient marker/polyline management
- Smooth animations and transitions
- Responsive UI adapts to screen size

## Troubleshooting

### Map not displaying
```
✓ Check internet connection (needs OpenStreetMap)
✓ Verify backend is running on http://localhost:8000
✓ Open browser console (F12) for errors
```

### No data showing
```
✓ Ensure backend is responding to /state endpoint
✓ Check response format matches expected schema
✓ Verify CORS is enabled on backend
```

### Updates not happening
```
✓ Check REFRESH_INTERVAL in app.js
✓ Monitor Network tab in DevTools
✓ Verify backend has signals in database
```

## Development Tips

### Debug Mode
Add this to `app.js` for detailed logging:
```javascript
// At top of app.js
const DEBUG = true;

function log(msg, data) {
    if (DEBUG) console.log(`[ISCS] ${msg}`, data || '');
}
```

### Testing with Sample Data
Modify `fetchStateData()` to use test data:
```javascript
const testData = {
    success: true,
    segments: [{
        segment: "Test Street",
        rsus: [{
            rsu_id: "TEST_RSU",
            lat: 31.9454,
            lng: 35.9284,
            avg_speed: 45.0,
            status: "moderate"
        }],
        edges: []
    }]
};
```

## API Status

The dashboard shows server connectivity:
- 🟢 Green: Backend online
- 🟡 Yellow: Connecting
- 🔴 Red: Offline

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Historical trend charts
- [ ] Alert notifications popup
- [ ] Export traffic reports
- [ ] Segment search/filter
- [ ] Custom color themes
- [ ] Mobile-optimized view
- [ ] Integration with external traffic APIs

## License

Part of the ISCS graduation project.
Jordan University of Science and Technology.

---

## Quick Start Command

```bash
# 1. Start backend server
cd backend_server/functions
python main.py

# 2. In another terminal, open web dashboard
cd web_dashboard
open index.html  # macOS
# OR
start index.html  # Windows
```

Then navigate to the dashboard and you should see live traffic data!