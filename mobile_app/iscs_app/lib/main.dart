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
  WidgetsBinding widgetsBinding = WidgetsFlutterBinding.ensureInitialized();
  FlutterNativeSplash.preserve(widgetsBinding: widgetsBinding);
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.system,
      theme: TAppTheme.lightTheme,
      darkTheme: TAppTheme.darkTheme,
    );
  }
}
