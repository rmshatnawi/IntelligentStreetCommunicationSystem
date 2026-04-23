import 'package:flutter/material.dart';

class TCheckboxTheme {
  TCheckboxTheme._(); // Private constructor to prevent instantiation

  static CheckboxThemeData lightCheckboxTheme = CheckboxThemeData(
    fillColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.blue; // Color for selected state
      } else {
        return Colors.transparent; // Default color for unselected state
      }
    }),
    checkColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.white; // Color for disabled state
      } else {
        return Colors.black; // Default color for enabled state
      }
    }),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
  );

  static CheckboxThemeData darkCheckboxTheme = CheckboxThemeData(
    fillColor: MaterialStateProperty.all(Colors.blue),
    checkColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.white; // Color for disabled state
      } else {
        return Colors.black; // Default color for enabled state
      }
    }),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
  );
}
