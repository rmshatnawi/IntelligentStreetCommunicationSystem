// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/theme/theme.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Assembles the complete ThemeData objects for light
//           and dark mode by composing all sub-theme classes.
//           This is the single file referenced in main.dart —
//           all theme changes go through sub-theme files in
//           the custom_theme/ folder, not here directly.
// ============================================================


import 'package:flutter/material.dart';
import 'package:iscs_app/utils/theme/custom_theme/text_theme.dart';

import 'package:iscs_app/utils/theme/custom_theme/appbar_theme.dart';
import 'package:iscs_app/utils/theme/custom_theme/bottom_sheet_theme.dart';
import 'package:iscs_app/utils/theme/custom_theme/checkbox_theme.dart';
import 'package:iscs_app/utils/theme/custom_theme/chip_theme.dart';
import 'package:iscs_app/utils/theme/custom_theme/elevated_button_theme.dart';
import 'package:iscs_app/utils/theme/custom_theme/text_field_theme.dart';
import 'package:iscs_app/utils/theme/custom_theme/outlined_button_theme.dart';

class TAppTheme {
  TAppTheme._(); // Private constructor to prevent instantiation

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'Poppins_Regular',
    brightness: Brightness.light,
    primaryColor: Colors.blue,
    textTheme: TTextTheme.lightTextTheme,
    chipTheme: TChipTheme.lightChipTheme,
    scaffoldBackgroundColor: Colors.white,
    elevatedButtonTheme: TElevatedButtonTheme.lightElevatedButtonTheme,
    checkboxTheme: TCheckboxTheme.lightCheckboxTheme,
    bottomSheetTheme: TBottomSheetTheme.lightBottomSheetTheme,
    outlinedButtonTheme: TOutlinedButtonTheme.lightOutlinedButtonTheme,
    appBarTheme: TAppBarTheme.lightAppBarTheme,
    inputDecorationTheme: TTextFieldTheme.lightTextFieldTheme,
  );
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'Poppins_Regular',
    brightness: Brightness.dark,
    primaryColor: Colors.blue,
    textTheme: TTextTheme.darkTextTheme,
    chipTheme: TChipTheme.darkChipTheme,
    scaffoldBackgroundColor: Colors.black,
    elevatedButtonTheme: TElevatedButtonTheme.darkElevatedButtonTheme,
    checkboxTheme: TCheckboxTheme.darkCheckboxTheme,
    bottomSheetTheme: TBottomSheetTheme.darkBottomSheetTheme,
    outlinedButtonTheme: TOutlinedButtonTheme.darkOutlinedButtonTheme,
    appBarTheme: TAppBarTheme.darkAppBarTheme,
    inputDecorationTheme: TTextFieldTheme.darkTextFieldTheme,
  );
}
