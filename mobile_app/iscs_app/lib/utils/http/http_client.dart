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

class THttpHelper {
  static String _baseUrl =
      'https://api.example.com'; // Replace with your API base URL

  //helper method for GET requests
  static Future<dynamic> get(String endpoint) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error making GET request: $e');
    }
  }

  //helper method for POST requests
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
        throw Exception('Failed to post data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error making POST request: $e');
    }
  }

  //handler for PUT requests
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
        throw Exception('Failed to update data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error making PUT request: $e');
    }
  }

  //handler for DELETE requests
  static Future<void> delete(String endpoint) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await http.delete(url);
      if (response.statusCode != 200) {
        throw Exception('Failed to delete data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error making DELETE request: $e');
    }
  }
}
