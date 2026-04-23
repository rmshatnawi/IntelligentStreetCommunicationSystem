// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/constants/sizes.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Defines all spacing, sizing, and layout constants.
//           All widgets must use these constants for padding,
//           margin, border radius, and font sizes — never use
//           raw numbers directly in widget files.
// ============================================================


import 'package:flutter/material.dart';
 
class TSizes {
  TSizes._(); // Private constructor — use as a constants namespace only
 
  // ─── PADDING & MARGIN ──────────────────────────────────────
  static const double xs  = 4.0;
  static const double sm  = 8.0;
  static const double md  = 16.0;
  static const double lg  = 24.0;
  static const double xl  = 32.0;
  static const double xxl = 48.0;
 
  // ─── ICON SIZES ────────────────────────────────────────────
  static const double iconXs = 12.0;
  static const double iconSm = 16.0;
  static const double iconMd = 24.0;
  static const double iconLg = 32.0;
 
  // ─── FONT SIZES ────────────────────────────────────────────
  static const double fontSm  = 12.0;
  static const double fontMd  = 14.0;
  static const double fontLg  = 16.0;
  static const double fontXl  = 18.0;
  static const double fontXxl = 24.0;
 
  // ─── BUTTON ────────────────────────────────────────────────
  static const double buttonHeight      = 50.0;
  static const double buttonRadius      = 12.0;
  static const double buttonWidth       = double.infinity;
  static const double buttonElevation   = 0.0;
 
  // ─── INPUT FIELD ───────────────────────────────────────────
  static const double inputFieldRadius  = 14.0;
  static const double inputFieldHeight  = 56.0;
 
  // ─── CARD ──────────────────────────────────────────────────
  static const double cardRadius        = 16.0;
  static const double cardElevation     = 2.0;
 
  // ─── BORDER RADIUS ─────────────────────────────────────────
  static const double borderRadiusSm   = 4.0;
  static const double borderRadiusMd   = 8.0;
  static const double borderRadiusLg   = 16.0;
 
  // ─── DIVIDER ───────────────────────────────────────────────
  static const double dividerHeight     = 1.0;
 
  // ─── IMAGE ─────────────────────────────────────────────────
  static const double imageThumbSize   = 80.0;
 
  // ─── APP BAR ───────────────────────────────────────────────
  static const double appBarHeight     = 56.0;
}

//padding and margin sizes
//icons sizes
//font sizes
//button sizes
//container sizes
//border radius 
//spaces between sections
//divider hights
//input field heights
//card sizes
//list item heights
//image carousel hight
//grid view spacing