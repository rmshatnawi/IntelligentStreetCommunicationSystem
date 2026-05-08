import 'package:flutter/material.dart';

class TCheckboxTheme {
  TCheckboxTheme._(); // Private constructor to prevent instantiation

  static CheckboxThemeData lightCheckboxTheme = CheckboxThemeData(
    fillColor: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return Colors.blue; // Color for selected state
      } else {
        return Colors.transparent; // Default color for unselected state
      }
    }),
    checkColor: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return Colors.white; // Color for disabled state
      } else {
        return Colors.black; // Default color for enabled state
      }
    }),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
  );

  static CheckboxThemeData darkCheckboxTheme = CheckboxThemeData(
    fillColor: WidgetStateProperty.all(Colors.blue),
    checkColor: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return Colors.white; // Color for disabled state
      } else {
        return Colors.black; // Default color for enabled state
      }
    }),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
  );
}
