// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/logging/logger.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Thin wrapper around the `logger` package.
//           Provides a single static logger instance used across
//           the entire app for consistent log formatting.
//           Use this instead of print() for all debug output.
//
//           Usage:
//             TLoggerHelper.logInfo('Signal fetched');
//             TLoggerHelper.logError('Failed to connect');
//             TLoggerHelper.logWarning('Retrying...');
// ============================================================

import 'package:logger/logger.dart';
 
class TLoggerHelper {
  TLoggerHelper._(); // Private constructor — use static methods only
 
  // Single shared Logger instance for the whole app
  static final Logger _logger = Logger();
 
  // ─── LOG LEVELS ──────────────────────────────────────────────
 
  // For general informational messages (e.g., screen loaded, data received)
  static void logInfo(String message) {
    _logger.i(message);
  }
 
  // For errors and exceptions (e.g., API failure, null data)
  static void logError(String message) {
    _logger.e(message);
  }
 
  // For non-critical warnings (e.g., empty list returned, slow response)
  static void logWarning(String message) {
    _logger.w(message);
  }
 
  // For verbose debug output during development only
  static void logDebug(String message) {
    _logger.d(message);
  }
}
