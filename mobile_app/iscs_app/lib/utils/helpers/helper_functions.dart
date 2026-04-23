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
