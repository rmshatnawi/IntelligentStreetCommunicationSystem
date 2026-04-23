// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/constants/text_strings.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Defines all UI-facing string literals used across
//           the app — button labels, titles, messages, errors.
//           Centralizing strings here makes future localization
//           (Arabic/English) easier to implement.
//           Never hardcode UI text directly in widget files.
// ============================================================


class TTexts {
  TTexts._(); // Private constructor — use as a constants namespace only
 
  // ─── APP ───────────────────────────────────────────────────
  static const String appName = 'ISCS';
  static const String appTagline = 'Intelligent Street Communication System';
 
  // ─── HOME SCREEN ───────────────────────────────────────────
  static const String homeTitle   = 'Live Traffic';
  static const String allSegments = 'All Segments';
 
  // ─── TRAFFIC STATUS LABELS ─────────────────────────────────
  // Must match the status strings returned by the backend /analyze endpoint
  static const String statusFree      = 'Free';
  static const String statusModerate  = 'Moderate';
  static const String statusCongested = 'Congested';
  static const String statusSevere    = 'Severe';
 
  // ─── ALERTS ────────────────────────────────────────────────
  static const String alertsTitle       = 'Active Alerts';
  static const String noAlertsMessage   = 'No active alerts at this time.';
 
  // ─── ERROR MESSAGES ────────────────────────────────────────
  static const String errorNetwork      = 'Cannot connect to server. Check your connection.';
  static const String errorNoData       = 'No data available for this segment.';
  static const String errorGeneric      = 'Something went wrong. Please try again.';
 
  // ─── BUTTONS ───────────────────────────────────────────────
  static const String btnRetry         = 'Retry';
  static const String btnViewDetails   = 'View Details';
  static const String btnDismiss       = 'Dismiss';
}
 
