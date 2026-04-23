import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

class THelperFunctions {
  static Color? getColor(String value) {
    if (value == "Green") {
      return Colors.green;
    } else if (value == "Red") {
      return Colors.red;
    } else if (value == "Yellow") {
      return Colors.yellow;
    } else {
      return null; // Default color or handle as needed
    }
  }

  //truncateText
  //isDarkMode
  //screenSize
  //navigateToScreen
  //screenWidth
  //screenHeight
  //getFormattedDate
  //removeDuplicates
  //wrapWidgets
}
