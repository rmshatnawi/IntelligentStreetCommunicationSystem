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
  static void hideKeyboard(BuildContext context) {
    FocusScope.of(context).requestFocus(FocusNode());
  }

  static Future<void> setStatusBarColor(Color color) async {
    // Set the status bar color
    SystemChrome.setSystemUIOverlayStyle(
      SystemUiOverlayStyle(statusBarColor: color),
    );
  }

  static bool isLandscapeOrientation(BuildContext context) {
    final viewInsets = View.of(context).viewInsets;
    return viewInsets.bottom == 0;
  }

  static bool isPortraitOrientation(BuildContext context) {
    final viewInsets = View.of(context).viewInsets;
    return viewInsets.bottom != 0;
  }

  static void setFullScreen(bool enable) {
    SystemChrome.setEnabledSystemUIMode(
      enable ? SystemUiMode.immersiveSticky : SystemUiMode.edgeToEdge,
    );
  }

  // Add more utility methods as needed, such as checking for specific device features, handling screen rotations, etc.
  static Future<bool> hasInternetConnection() async {
    try {
      final result = await InternetAddress.lookup('example.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException catch (_) {
      return false;
    }
  }

  static bool isAndroid() {
    return Platform.isAndroid;
  }

  //static void launchURL(String url) async {
  // if (await canLaunchUrlString(url)) {
  //   await launchUrlString(url);
  // } else {
  //   throw 'Could not launch $url';
  //  }
  //  }
}
