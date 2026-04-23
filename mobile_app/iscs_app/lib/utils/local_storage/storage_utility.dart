// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/local_storage/storage_utility.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Provides persistent key-value local storage using
//           the get_storage package.
//           Used to store user preferences (e.g., theme mode,
//           last-viewed segment) that must survive app restarts.
//
//           This is a singleton — always access via TLocalStorage().
//           Call init() once in main() before runApp() if needed.
//
//           Usage:
//             final storage = TLocalStorage();
//             await storage.write('theme', 'dark');
//             final theme = storage.read('theme'); // 'dark'
// ============================================================

import 'package:get_storage/get_storage.dart';

class TLocalStorage {
  static TLocalStorage? _instance;

  factory TLocalStorage() {
    return _instance ??= TLocalStorage._internal();
  }

  TLocalStorage._internal();

  final _storage = GetStorage();

  Future<void> init() async {
    await GetStorage.init();
  }

  Future<void> write(String key, dynamic value) async {
    await _storage.write(key, value);
  }

  dynamic read(String key) {
    return _storage.read(key);
  }

  Future<void> remove(String key) async {
    await _storage.remove(key);
  }

  Future<void> clear() async {
    await _storage.erase();
  }
}
