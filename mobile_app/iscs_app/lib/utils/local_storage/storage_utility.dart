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
  // Singleton instance
  static TLocalStorage? _instance;
 
  // Factory constructor returns the same instance every time
  factory TLocalStorage() {
    return _instance ??= TLocalStorage._internal();
  }
 
  TLocalStorage._internal();
 
  // Underlying get_storage instance
  final _storage = GetStorage();
 
  // ─── INIT ────────────────────────────────────────────────────
  // Must be called before first use if this is your first GetStorage access.
  // Safe to call multiple times — it is idempotent.
  Future<void> init() async {
    await GetStorage.init();
  }
 
  // ─── WRITE ───────────────────────────────────────────────────
  // Persists a value under the given key.
  // Supports: String, int, double, bool, Map, List
  Future<void> write(String key, dynamic value) async {
    await _storage.write(key, value);
  }
 
  // ─── READ ────────────────────────────────────────────────────
  // Retrieves a value by key. Returns null if key does not exist.
  dynamic read(String key) {
    return _storage.read(key);
  }
 
  // ─── REMOVE ──────────────────────────────────────────────────
  // Deletes a single key-value pair.
  Future<void> remove(String key) async {
    await _storage.remove(key);
  }
 
  // ─── CLEAR ───────────────────────────────────────────────────
  // Deletes ALL stored data. Use with caution.
  // Suitable for logout / reset flows.
  Future<void> clear() async {
    await _storage.erase();
  }
}
 
