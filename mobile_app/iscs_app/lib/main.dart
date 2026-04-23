// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/main.dart
// Author:   Raghad Shatnawi
// Last Modified: April 2026
// Purpose:  Entry point of the Flutter application.
//           Initializes the native splash screen, applies
//           the app theme (light/dark), and launches the
//           root MaterialApp widget.
//           No home screen is set yet — add a home: route
//           once the first screen is implemented.
// ============================================================


import 'package:flutter/material.dart';
import 'package:flutter_native_splash/flutter_native_splash.dart';
import 'package:iscs_app/utils/theme/theme.dart';
 
void main() {
  // Ensure Flutter engine is initialized before runApp.
  // Required when calling native code (e.g., splash, Firebase) before the app starts.
  WidgetsBinding widgetsBinding = WidgetsFlutterBinding.ensureInitialized();
 
  // Keeps the splash screen visible until FlutterNativeSplash.remove() is called.
  // Call FlutterNativeSplash.remove() after your initialization logic completes
  // (e.g., after loading user session, fetching config, etc.)
  FlutterNativeSplash.preserve(widgetsBinding: widgetsBinding);
 
  runApp(const App());
}
 
// ─── App ─────────────────────────────────────────────────────
// Root widget. Sets up MaterialApp with light/dark theming.
// Does NOT define a home screen yet — this must be added.
class App extends StatelessWidget {
  const App({super.key});
 
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
 
      // Follows the device OS theme setting (light or dark)
      themeMode: ThemeMode.system,
 
      // Defined in lib/utils/theme/theme.dart
      theme: TAppTheme.lightTheme,
      darkTheme: TAppTheme.darkTheme,
 
      // TODO: Add home: or initialRoute: once the first screen is built
      // Example: home: const HomeScreen(),
    );
  }
}
