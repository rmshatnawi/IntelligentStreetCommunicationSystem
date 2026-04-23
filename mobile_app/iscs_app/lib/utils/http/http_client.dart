// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/utils/http/http_client.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Generic HTTP wrapper for communicating with the
//           FastAPI backend server.
//           Provides GET, POST, PUT, DELETE methods.
//           All API calls in the app must go through this class.
//           Base URL is read from TApiConstants — never hardcode
//           URLs here or in any other file.
// ============================================================

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:iscs_app/utils/constants/api_constants.dart';
 
class THttpHelper {
  THttpHelper._(); // Private constructor — use static methods only
 
  // Base URL sourced from api_constants.dart
  static const String _baseUrl = TApiConstants.baseUrl;
 
  // ─── GET ─────────────────────────────────────────────────────
  // Fetches data from the server.
  // endpoint: path after the base URL, e.g. '/signals'
  // Returns: decoded JSON (Map or List)
  // Throws: Exception on non-200 status or network failure
  static Future<dynamic> get(String endpoint) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('GET failed: ${response.statusCode} — $endpoint');
      }
    } catch (e) {
      throw Exception('GET error on $endpoint: $e');
    }
  }
 
  // ─── POST ────────────────────────────────────────────────────
  // Sends data to the server.
  // endpoint: path after the base URL
  // data: map to serialize as JSON body
  // Returns: decoded JSON response body
  // Throws: Exception on non-200/201 status or network failure
  static Future<dynamic> post(
    String endpoint,
    Map<String, dynamic> data,
  ) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await http.post(
        url,
        body: jsonEncode(data),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('POST failed: ${response.statusCode} — $endpoint');
      }
    } catch (e) {
      throw Exception('POST error on $endpoint: $e');
    }
  }
 
  // ─── PUT ─────────────────────────────────────────────────────
  // Updates an existing resource on the server.
  // endpoint: path after the base URL
  // data: map of updated fields
  static Future<dynamic> put(String endpoint, Map<String, dynamic> data) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await http.put(
        url,
        body: jsonEncode(data),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('PUT failed: ${response.statusCode} — $endpoint');
      }
    } catch (e) {
      throw Exception('PUT error on $endpoint: $e');
    }
  }
 
  // ─── DELETE ──────────────────────────────────────────────────
  // Deletes a resource on the server.
  // endpoint: path after the base URL including resource ID
  static Future<void> delete(String endpoint) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await http.delete(url);
      if (response.statusCode != 200) {
        throw Exception('DELETE failed: ${response.statusCode} — $endpoint');
      }
    } catch (e) {
      throw Exception('DELETE error on $endpoint: $e');
    }
  }
}
 
