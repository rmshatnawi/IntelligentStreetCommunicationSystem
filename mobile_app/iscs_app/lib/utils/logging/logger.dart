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
