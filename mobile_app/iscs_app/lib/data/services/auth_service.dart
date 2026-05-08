// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/data/services/auth_service.dart
// Author:   Raghad Shatnawi
// Last Modified: 9 May 2026
// Purpose:  Singleton service wrapping Firebase Auth.
//           All screens and controllers interact with
//           Firebase Auth only through this class.
// ============================================================

import 'package:firebase_auth/firebase_auth.dart';

class AuthService {
  // ─── Singleton ───────────────────────────────────────────
  AuthService._internal();
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;

  final FirebaseAuth _auth = FirebaseAuth.instance;

  // ─── Getters ─────────────────────────────────────────────

  /// Currently signed-in user, or null.
  User? get currentUser => _auth.currentUser;

  /// Stream that emits on sign-in / sign-out events.
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  // ─── Sign In ─────────────────────────────────────────────

  /// Signs in with email and password.
  /// Throws a human-readable [String] on failure.
  Future<UserCredential> signIn(String email, String password) async {
    try {
      return await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
    } on FirebaseAuthException catch (e) {
      throw _readableMessage(e.code);
    }
  }

  // ─── Sign Out ────────────────────────────────────────────

  /// Signs out the current user.
  Future<void> signOut() async {
    await _auth.signOut();
  }

  // ─── ID Token ────────────────────────────────────────────

  /// Returns the current user's Firebase ID token.
  /// Throws if no user is logged in.
  /// [forceRefresh] — set true to force a token refresh
  /// (used by THttpHelper on 401 retry).
  Future<String> getIdToken({bool forceRefresh = false}) async {
    final user = _auth.currentUser;
    if (user == null) {
      throw 'No user is currently signed in. Please log in first.';
    }

    final token = await user.getIdToken(forceRefresh);
    if (token == null) {
      throw 'Failed to retrieve ID token. Please log in again.';
    }

    return token;
  }

  // ─── Error Mapping ───────────────────────────────────────

  /// Converts FirebaseAuthException error codes to
  /// user-facing messages.
  String _readableMessage(String code) {
    switch (code) {
      case 'invalid-email':
        return 'The email address is not valid.';
      case 'user-disabled':
        return 'This account has been disabled. Contact support.';
      case 'user-not-found':
        return 'No account found with this email.';
      case 'wrong-password':
        return 'Incorrect password. Please try again.';
      case 'invalid-credential':
        return 'Invalid credentials. Please check your email and password.';
      case 'too-many-requests':
        return 'Too many failed attempts. Please try again later.';
      case 'network-request-failed':
        return 'Network error. Check your internet connection.';
      case 'operation-not-allowed':
        return 'Email/password sign-in is not enabled for this project.';
      default:
        return 'Authentication failed ($code). Please try again.';
    }
  }
}