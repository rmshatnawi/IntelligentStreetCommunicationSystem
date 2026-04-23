
// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/validators/validation.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Provides form field validator functions.
//           Each method returns null if the input is valid,
//           or a String error message if it is not.
//           Pass these directly to TextFormField's validator:
//
//           TextFormField(
//             validator: TValidator.validateEmail,
//           )
// ============================================================

class TValidator {
  TValidator._(); // Private constructor — use static methods only
 
  // ─── EMAIL ───────────────────────────────────────────────────
  // Validates email format using a standard regex.
  // Returns null on valid input, error string otherwise.
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email cannot be empty';
    }
    final pattern = r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$';
    final regex = RegExp(pattern);
    if (!regex.hasMatch(value)) {
      return 'Please enter a valid email address';
    }
    return null;
  }
 
  // ─── PASSWORD ────────────────────────────────────────────────
  // Validates password minimum length (6 characters).
  // Returns null on valid input, error string otherwise.
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password cannot be empty';
    }
    if (value.length < 6) {
      return 'Password must be at least 6 characters long';
    }
    return null;
  }
 
  // ─── REQUIRED FIELD ──────────────────────────────────────────
  // Generic non-empty check for any required field.
  // Pass fieldName to customize the error message.
  static String? validateRequired(String? value, {String fieldName = 'Field'}) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName cannot be empty';
    }
    return null;
  }
}
 
