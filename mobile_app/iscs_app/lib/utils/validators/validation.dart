
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
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return "Email cannot be empty";
    }
    //regex for email validation
    String pattern = r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$';
    RegExp regex = RegExp(pattern);
    if (!regex.hasMatch(value)) {
      return "Please enter a valid email address";
    }
    return null;
  }

  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return "Password cannot be empty";
    }
    if (value.length < 6) {
      return "Password must be at least 6 characters long";
    }
    return null;
  }

  // Add more validation methods as needed, such as for phone numbers, usernames, etc.
}
