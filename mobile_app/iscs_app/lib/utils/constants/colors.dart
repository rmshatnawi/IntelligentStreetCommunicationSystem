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
  TColors._(); // Private constructor to prevent instantiation
  //app basic colors
  static const Color primary = Color(0xFF4b68ff);
  static const Color secondary = Colors.green;
  static const Color background = Colors.white;
  static const Color surface = Colors.grey;
  static const Color error = Colors.red;
  static const Color accent = Colors.white;
  //Text Colors
  static const Color textPrimary = Colors.white;
  static const Color textSecondary = Colors.white;
  static const Color textBackground = Colors.black;
  static const Color textSurface = Colors.black;
  static const Color textError = Colors.white;

  //background colors
  static const Color lightBackground = Colors.white;
  static const Color darkBackground = Colors.black;

  //background container colors
  static const Color lightContainerBackground = Colors.white;
  static const Color darkContainerBackground = Colors.grey;

  //gradiant colors
  static const List<Color> gradientColors = [
    Color(0xFF4b68ff),
    Color(0xFF4b68ff),
  ];
}
