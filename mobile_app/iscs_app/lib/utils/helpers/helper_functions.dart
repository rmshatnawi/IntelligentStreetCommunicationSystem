// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/helpers/helper_functions.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  General utility helper functions used across screens.
//           Functions here are stateless and have no side effects —
//           they take input and return output.
//           All screen-level logic belongs in controllers, not here.
// ============================================================

import 'package:flutter/material.dart';
import 'package:iscs_app/utils/constants/colors.dart';
import 'package:iscs_app/utils/constants/enums.dart';
 
class THelperFunctions {
  THelperFunctions._(); // Private constructor — use static methods only
 
  // ─── TRAFFIC STATUS COLOR ────────────────────────────────────
  // Maps a backend traffic status string to a display color.
  // Used by map markers and alert cards.
  // Must match the status strings from the backend /analyze endpoint.
  static Color getTrafficStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'free':
        return TColors.trafficFree;
      case 'moderate':
        return TColors.trafficModerate;
      case 'congested':
        return TColors.trafficCongested;
      case 'severe':
        return TColors.trafficSevere;
      default:
        return Colors.grey;
    }
  }
 
  // ─── TRAFFIC STATUS ENUM ─────────────────────────────────────
  // Converts a backend status string to the TrafficStatus enum.
  // Use this when you need type-safe conditional logic.
  static TrafficStatus parseTrafficStatus(String status) {
    switch (status.toLowerCase()) {
      case 'free':      return TrafficStatus.free;
      case 'moderate':  return TrafficStatus.moderate;
      case 'congested': return TrafficStatus.congested;
      case 'severe':    return TrafficStatus.severe;
      default:          return TrafficStatus.free;
    }
  }
 
  // ─── DARK MODE CHECK ─────────────────────────────────────────
  // Returns true if the current device theme is dark mode.
  static bool isDarkMode(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark;
  }
 
  // ─── SCREEN SIZE ─────────────────────────────────────────────
  static double screenWidth(BuildContext context) =>
      MediaQuery.of(context).size.width;
 
  static double screenHeight(BuildContext context) =>
      MediaQuery.of(context).size.height;
 
  // ─── TEXT TRUNCATION ─────────────────────────────────────────
  // Truncates a string to maxLength and appends '...' if needed.
  // Used for segment names or alert messages in compact cards.
  static String truncateText(String text, int maxLength) {
    if (text.length <= maxLength) return text;
    return '${text.substring(0, maxLength)}...';
  }
 
  // ─── DATE FORMAT ─────────────────────────────────────────────
  // Formats an ISO 8601 datetime string (from the backend) into
  // a readable format: 'Apr 23, 2026 at 14:30'
  static String formatTimestamp(String isoString) {
    try {
      final dt = DateTime.parse(isoString).toLocal();
      final months = ['Jan','Feb','Mar','Apr','May','Jun',
                      'Jul','Aug','Sep','Oct','Nov','Dec'];
      final hour   = dt.hour.toString().padLeft(2, '0');
      final minute = dt.minute.toString().padLeft(2, '0');
      return '${months[dt.month - 1]} ${dt.day}, ${dt.year} at $hour:$minute';
    } catch (_) {
      return isoString; // return raw string if parse fails
    }
  }
}
 
