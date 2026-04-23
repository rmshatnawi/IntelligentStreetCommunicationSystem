// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/formatters/formatter.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Provides formatting utilities for dates, times,
//           currency, and numbers.
//           Used across the app wherever raw values from the
//           backend need to be presented in a readable format.
//           All formatting logic lives here — never format
//           display values inline inside widget build methods.
// ============================================================
 
class TFormatter {
  TFormatter._(); // Private constructor — use static methods only
 
  // ─── DATE ────────────────────────────────────────────────────
  // Formats a DateTime object as 'dd/MM/yyyy'.
  // Example: DateTime(2026, 4, 23) → '23/04/2026'
  // Used for displaying signal or alert timestamps in a date-only context.
  static String formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/'
           '${date.month.toString().padLeft(2, '0')}/'
           '${date.year}';
  }
 
  // ─── TIME ────────────────────────────────────────────────────
  // Formats a TimeOfDay object as 'hh:mm AM/PM'.
  // Example: TimeOfDay(hour: 14, minute: 5) → '02:05 PM'
  // Used when displaying the time portion of a signal or alert.
  static String formatTime(TimeOfDay time) {
    final hour   = time.hourOfPeriod == 0 ? 12 : time.hourOfPeriod;
    final period = time.period == DayPeriod.am ? 'AM' : 'PM';
    return '${hour.toString().padLeft(2, '0')}:'
           '${time.minute.toString().padLeft(2, '0')} $period';
  }
 
  // ─── DATE + TIME ─────────────────────────────────────────────
  // Combines formatDate and formatTime into a single string.
  // Example: '23/04/2026 02:05 PM'
  // Use this for full timestamps on signal or alert detail screens.
  static String formatDateTime(DateTime dateTime) {
    return '${formatDate(dateTime)} ${formatTime(TimeOfDay.fromDateTime(dateTime))}';
  }
 
  // ─── CURRENCY ────────────────────────────────────────────────
  // Formats a double as a currency string.
  // Example: 1500.5 → '$1,500.50' (default US locale)
  // Not currently used by ISCS — retained for potential future
  // features such as fine amounts or subscription pricing.
  static String formatCurrency(
    double amount, {
    String locale = 'en_US',
    String symbol = '\$',
  }) {
    final format = NumberFormat.currency(locale: locale, symbol: symbol);
    return format.format(amount);
  }
 
  // ─── NUMBER ──────────────────────────────────────────────────
  // Formats a number with locale-appropriate thousands separators.
  // Example: 1500000 → '1,500,000'
  // Use this when displaying vehicle counts or signal counts.
  static String formatNumber(num number, {String locale = 'en_US'}) {
    final format = NumberFormat.decimalPattern(locale);
    return format.format(number);
  }
 
  // ─── SPEED ───────────────────────────────────────────────────
  // Formats a speed value with the km/h unit appended.
  // Example: 42.5 → '42.5 km/h'
  // Use this when displaying average speed on signal or analysis cards.
  static String formatSpeed(double speed) {
    return '${speed.toStringAsFixed(1)} km/h';
  }
}
 
