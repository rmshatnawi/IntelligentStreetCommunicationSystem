// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/device/device_utility.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Provides device-level utility methods used across
//           the app — keyboard dismissal, status bar color,
//           orientation checks, fullscreen toggle, and
//           internet connectivity checking.
//
// ============================================================


import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
 
class TDeviceUtility {
  TDeviceUtility._(); // Private constructor — use static methods only
 
  // ─── KEYBOARD ────────────────────────────────────────────────
  // Dismisses the on-screen keyboard.
  // Call when tapping outside a text field.
  static void hideKeyboard(BuildContext context) {
    FocusScope.of(context).requestFocus(FocusNode());
  }
 
  // ─── STATUS BAR ──────────────────────────────────────────────
  // Changes the status bar background color.
  // Useful when navigating to screens with a colored header.
  static Future<void> setStatusBarColor(Color color) async {
    SystemChrome.setSystemUIOverlayStyle(
      SystemUiOverlayStyle(statusBarColor: color),
    );
  }
 
  // ─── ORIENTATION ─────────────────────────────────────────────
  // Returns true if the device is in landscape orientation.
  static bool isLandscapeOrientation(BuildContext context) {
    final viewInsets = View.of(context).viewInsets;
    return viewInsets.bottom == 0;
  }
 
  // Returns true if the device is in portrait orientation.
  static bool isPortraitOrientation(BuildContext context) {
    final viewInsets = View.of(context).viewInsets;
    return viewInsets.bottom != 0;
  }
 
  // ─── FULLSCREEN ──────────────────────────────────────────────
  // Toggles fullscreen (hides/shows system UI bars).
  // Pass true to enter fullscreen, false to exit.
  static void setFullScreen(bool enable) {
    SystemChrome.setEnabledSystemUIMode(
      enable ? SystemUiMode.immersiveSticky : SystemUiMode.edgeToEdge,
    );
  }
 
  // ─── CONNECTIVITY ────────────────────────────────────────────
  // Checks for active internet connection.
  // Returns true if connected, false otherwise.
  // Use before making API calls to give the user a meaningful error.
  static Future<bool> hasInternetConnection() async {
    try {
      final result = await InternetAddress.lookup('example.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException catch (_) {
      return false;
    }
  }
 
  // ─── PLATFORM ────────────────────────────────────────────────
  // Returns true if running on Android.
  // Use for platform-specific behavior (e.g., back button handling).
  static bool isAndroid() {
    return Platform.isAndroid;
  }
}
 
