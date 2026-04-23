// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/constants/enums.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Defines all app-wide enumerations.
//           Using enums instead of raw strings prevents typos
//           and makes conditionals type-safe.
// ============================================================


// ─── TextSizes ───────────────────────────────────────────────
// Used to pass a size intent to reusable text widgets
// instead of hardcoding font sizes directly.
enum TextSizes { small, medium, large, extraLarge }
 
// ─── TrafficStatus ───────────────────────────────────────────
// Mirrors the backend traffic status strings from analyze.py.
// Used to drive UI color and icon choices on the map screen.
enum TrafficStatus { free, moderate, congested, severe }
