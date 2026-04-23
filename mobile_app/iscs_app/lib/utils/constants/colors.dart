// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/constants/colors.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Defines all brand and UI colors used across the app.
//           All widgets must reference colors from here — never
//           use hardcoded Color() values in widget files.
//           Each color has a light and dark mode variant where needed.
// ============================================================

 
import 'package:flutter/material.dart';
 
class TColors {
  TColors._(); // Private constructor — use as a constants namespace only
 
  // ─── BRAND COLORS ──────────────────────────────────────────
  // Primary brand color used for buttons, highlights, active states
  static const Color primary = Color(0xFF4b68ff);
 
  // Secondary color used for success states, online indicators
  static const Color secondary = Colors.green;
 
  // Accent color for overlays or contrast elements
  static const Color accent = Colors.white;
 
  // ─── SEMANTIC COLORS ───────────────────────────────────────
  // Used for error messages, failed states, severe alerts
  static const Color error = Colors.red;
 
  // ─── BACKGROUND COLORS ─────────────────────────────────────
  static const Color background    = Colors.white;
  static const Color lightBackground = Colors.white;
  static const Color darkBackground  = Colors.black;
 
  // ─── SURFACE / CONTAINER COLORS ────────────────────────────
  // Used for cards, panels, and containers
  static const Color surface = Colors.grey;
  static const Color lightContainerBackground = Colors.white;
  static const Color darkContainerBackground  = Colors.grey;
 
  // ─── TEXT COLORS ───────────────────────────────────────────
  // Primary text — used on colored/dark backgrounds
  static const Color textPrimary    = Colors.white;
  static const Color textSecondary  = Colors.white;
 
  // Text on light/white backgrounds
  static const Color textBackground = Colors.black;
  static const Color textSurface    = Colors.black;
 
  // Text used on error-colored backgrounds
  static const Color textError = Colors.white;
 
  // ─── TRAFFIC STATUS COLORS ─────────────────────────────────
  // Used in the map and alert cards to represent traffic severity
  static const Color trafficFree      = Color(0xFF4CAF50); // green
  static const Color trafficModerate  = Color(0xFFFF9800); // orange
  static const Color trafficCongested = Color(0xFFF44336); // red
  static const Color trafficSevere    = Color(0xFF9C27B0); // purple
 
  // ─── GRADIENT ──────────────────────────────────────────────
  // Used for gradient backgrounds or hero sections
  static const List<Color> gradientColors = [
    Color(0xFF4b68ff),
    Color(0xFF4b68ff),
  ];
}
 
