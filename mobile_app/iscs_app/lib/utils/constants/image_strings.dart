// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/constants/image_strings.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Defines all asset path strings for images and logos.
//           All Image.asset() calls must reference these constants
//           instead of hardcoding paths in widget files.
//           All paths must match what is declared in pubspec.yaml
//           under flutter > assets.
// ============================================================


class TImageStrings {
  TImageStrings._(); // Private constructor — use as a constants namespace only
 
  // ─── APP LOGOS ─────────────────────────────────────────────
  // Used in splash screen and onboarding
  static const String lightLogo = 'assets/logos/light_logo.png';
  static const String darkLogo  = 'assets/logos/dark_logo.png';
 
  // ─── ONBOARDING / ILLUSTRATIONS ────────────────────────────
  // Add paths here as new screens are built
  // static const String onboardingTraffic = 'assets/images/onboarding_traffic.png';
 
  // ─── MAP MARKERS ───────────────────────────────────────────
  // Custom pin icons for the traffic map
  // static const String markerFree      = 'assets/icons/marker_free.png';
  // static const String markerCongested = 'assets/icons/marker_congested.png';
}

//app logos
//social logos