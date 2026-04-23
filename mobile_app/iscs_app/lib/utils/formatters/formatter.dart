import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class TFormatter {
  static String formatDate(DateTime date) {
    // Format the date as needed, e.g., "dd/MM/yyyy"
    return "${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}";
  }

  static String formatterCurrency(
    double amount, {
    String locale = 'en_US',
    String symbol = '\$',
  }) {
    final format = NumberFormat.currency(locale: locale, symbol: symbol);
    return format.format(amount);
  }

  static String formatNumber(num number, {String locale = 'en_US'}) {
    final format = NumberFormat.decimalPattern(locale);
    return format.format(number);
  }

  static String formatTime(TimeOfDay time) {
    // Format the time as needed, e.g., "hh:mm AM/PM"
    final hour = time.hourOfPeriod == 0 ? 12 : time.hourOfPeriod;
    final period = time.period == DayPeriod.am ? "AM" : "PM";
    return "${hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')} $period";
  }

  static String formatDateTime(DateTime dateTime) {
    // Combine date and time formatting
    return "${formatDate(dateTime)} ${formatTime(TimeOfDay.fromDateTime(dateTime))}";
  }

  // Add more formatting methods as needed, such as for currency, numbers, etc.
}
