// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/constants/api_constants.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Defines the base server URL and all API endpoint
//           paths used by the Flutter app to communicate
//           with the FastAPI backend.
//           THttpHelper (http_client.dart) must read its base
//           URL from here — never hardcode URLs elsewhere.
// ============================================================


class TApiConstants {
 
  TApiConstants._(); // Private constructor — use as a constants namespace only
 
  // ─── BASE URL ──────────────────────────────────────────────
  // Change this to the deployed server URL before release.
  // During development: http://10.0.2.2:8000 for Android emulator
  //                     http://localhost:8000 for iOS simulator
  static const String baseUrl = 'http://10.0.2.2:8000';
 
  // ─── SIGNAL ENDPOINTS ──────────────────────────────────────
  // Returns the last 20 signals across all segments
  static const String signals = '/signals';
 
  // Returns the last 10 signals for a specific segment
  // Usage: '$signalsBySegment/Petra St'
  static const String signalsBySegment = '/signals';
 
  // ─── ALERT ENDPOINTS ───────────────────────────────────────
  // Returns the last 10 active alerts across all segments
  static const String alerts = '/alerts';
 
  // Returns the last 5 alerts for a specific segment
  // Usage: '$alertsBySegment/Petra St'
  static const String alertsBySegment = '/alerts';
 
  // ─── ANALYSIS ENDPOINTS ────────────────────────────────────
  // Triggers traffic analysis for a specific segment
  // Usage: '$analyze/Petra St'
  static const String analyze = '/analyze';
 
  // ─── HEALTH ────────────────────────────────────────────────
  // Server health check — use to test connectivity
  static const String health = '/health';
}
 
