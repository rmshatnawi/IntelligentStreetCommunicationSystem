import 'package:flutter/material.dart';

class AppTheme {
  AppTheme._();

  static const Color primary = Color(0xFFF48C55);
  static const Color secondary = Color(0xFF15255B);
  static const Color accent = Color(0xFFAB6D5B);

  static const Color background = Color.fromARGB(255, 225, 214, 200);
  static const Color surface = Color(0xFFE8D2C0);
  static const Color interactive = Color(0xFF486090);
  static const Color enabled = Color.fromARGB(255, 84, 93, 95);

  static const Color textPrimary = Color(0xFF403A43);
  static const Color textSecondary = Color(0xFF8A93AD);

  static const Color border = Color.fromARGB(255, 52, 64, 103);

  static const Color congested = Color(0xFFE24B4A);
  static const Color moderate = Color(0xFFEF9F27);
  static const Color clear = Color(0xFF639922);

  //spacing scale
  static const double space2 = 2;
  static const double space4 = 4;
  static const double space8 = 8;
  static const double space12 = 12;
  static const double space16 = 16;
  static const double space24 = 24;
  static const double space32 = 32;
  static const double space48 = 48;
  static const double space64 = 64;
  static const double space96 = 96;
  static const double space128 = 128;
  static const double space192 = 192;
  static const double space256 = 256;

  //borders, radius, elevation
  static const double radiusSmall = 6;
  static const double radiusMedium = 12;
  static const double radiusLarge = 20;

  static const double borderWidth = 1;
  static const double borderWidthFocused = 1.5;

  static const double elevationSmall = 2;
  static const double elevationMedium = 6;

  static ThemeData light = ThemeData(
    useMaterial3: true,
    scaffoldBackgroundColor: background,
    colorScheme: const ColorScheme(
      brightness: Brightness.light,
      primary: primary,
      onPrimary: Colors.white,
      secondary: secondary,
      onSecondary: Colors.white,
      error: congested,
      onError: Colors.white,
      surface: surface,
      onSurface: textPrimary,
    ),
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: secondary,
      ),

      displayMedium: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: secondary,
      ),

      titleLarge: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: secondary,
      ),

      titleMedium: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: textPrimary,
      ),

      bodyLarge: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: textPrimary,
      ),

      bodyMedium: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: textPrimary,
      ),

      bodySmall: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.normal,
        color: textSecondary,
      ),

      labelLarge: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: Colors.white,
      ),

      labelMedium: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: textSecondary,
      ),
    ),

    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,

      isDense: true,
      alignLabelWithHint: true,

      contentPadding: const EdgeInsets.symmetric(
        horizontal: space16,
        vertical: space16,
      ),

      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusLarge),
        borderSide: const BorderSide(color: border, width: 1),
      ),

      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusLarge),
        borderSide: const BorderSide(color: border, width: 1),
      ),

      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(radiusLarge),
        borderSide: const BorderSide(color: secondary, width: 2),
      ),

      hintStyle: const TextStyle(color: textSecondary, fontSize: 14),

      hintMaxLines: 1,
    ),

    appBarTheme: const AppBarTheme(
      backgroundColor: background,
      foregroundColor: secondary,
      elevation: 0,
    ),

    dividerColor: border,
  );
}
