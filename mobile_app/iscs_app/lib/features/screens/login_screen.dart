// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/features/authentication/screens/login_screen.dart
// Author:   Raghad Shatnawi
// Last Modified: 9 May 2026
// Purpose:  Login screen with email/password fields, sign-in
//           button, forgot password link, and sign-up button.
//           Uses the app's existing theme system — all colors
//           and text styles come from Theme.of(context).
//           Controller wiring will be added in Task 1.5.
// ============================================================

import 'package:flutter/material.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ─── Logo + App Name ─────────────────────────
                Center(
                  child: Column(
                    children: [
                      // App logo — replace asset path if different
                      Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          color: const Color(0xFF1B2A4A),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        // If you have a logo asset, use:
                        // child: Image.asset('assets/logos/logo.png'),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Smart Street',
                        style: theme.textTheme.headlineMedium,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 40),

                // ─── Email Field ─────────────────────────────
                Text(
                  'Email',
                  style: theme.textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                TextFormField(
                  keyboardType: TextInputType.emailAddress,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    hintText: 'Value',
                  ),
                ),

                const SizedBox(height: 20),

                // ─── Password Field ──────────────────────────
                Text(
                  'Password',
                  style: theme.textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                TextFormField(
                  obscureText: true,
                  textInputAction: TextInputAction.done,
                  decoration: const InputDecoration(
                    hintText: 'Value',
                  ),
                ),

                const SizedBox(height: 24),

                // ─── Sign In Button ──────────────────────────
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      // TODO: Task 1.5 — wire to AuthController.signIn()
                    },
                    child: const Text('Sign In'),
                  ),
                ),

                const SizedBox(height: 12),

                // ─── Forgot Password ─────────────────────────
                GestureDetector(
                  onTap: () {
                    // TODO: navigate to forgot password screen
                  },
                  child: Text(
                    'Forgot password?',
                    style: theme.textTheme.titleSmall?.copyWith(
                      decoration: TextDecoration.underline,
                    ),
                  ),
                ),

                const SizedBox(height: 28),

                // ─── Divider with "or" ───────────────────────
                Row(
                  children: [
                    const Expanded(child: Divider()),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'or',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                      ),
                    ),
                    const Expanded(child: Divider()),
                  ],
                ),

                const SizedBox(height: 28),

                // ─── Sign Up Button ──────────────────────────
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    onPressed: () {
                      // TODO: navigate to sign-up screen (if needed)
                    },
                    child: const Text('Sign up'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}