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
  static final Logger _logger = Logger();

  static void logInfo(String message) {
    _logger.i(message);
  }

  static void logError(String message) {
    _logger.e(message);
  }

  static void logWarning(String message) {
    _logger.w(message);
  }

  //debug,info,
  // Add more helper methods as needed, such as logging with different levels, formatting messages, etc.
}
