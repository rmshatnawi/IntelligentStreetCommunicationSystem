// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/features/authentication/screens/auth_gate.dart
// Author:   Raghad Shatnawi
// Last Modified: 9 May 2026
// Purpose:  Listens to Firebase auth state and routes to
//           LoginScreen or HomeScreen accordingly.
//           Dismisses the native splash screen exactly once
//           after the first auth state emission.
// ============================================================

import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_native_splash/flutter_native_splash.dart';

import 'package:iscs_app/data/services/auth_service.dart';
// TODO: replace these placeholder imports with actual screen paths
// once LoginScreen and HomeScreen are built.
import 'package:iscs_app/features/authentication/screens/login_screen.dart';
import 'package:iscs_app/features/home/screens/home_screen.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  /// Ensures FlutterNativeSplash.remove() is called only once.
  static bool _splashRemoved = false;

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: AuthService().authStateChanges,
      builder: (context, snapshot) {
        // ── Still waiting for the first emission ──
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // ── First emission received — dismiss splash once ──
        if (!_splashRemoved) {
          FlutterNativeSplash.remove();
          _splashRemoved = true;
        }

        // ── Route based on auth state ──
        if (snapshot.data == null) {
          return const LoginScreen();
        } else {
          return const HomeScreen();
        }
      },
    );
  }
}