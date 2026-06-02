import 'package:app/app_theme.dart';
import 'package:app/pages/Registeration.dart';
import 'package:app/pages/home_page.dart';
import 'package:app/pages/signin_page.dart';
import 'package:app/pages/welcome_page.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Intelligent Street Communication System App',
      theme: AppTheme.light,
      debugShowCheckedModeBanner: false,
      // home: WelcomePage(),
      // home: RegisterationPage(),
      // home: SignInPage(),
      initialRoute: WelcomePage().routeName,
      routes: {
        WelcomePage().routeName: (context) => const WelcomePage(),
        SignInPage().routeName: (context) => const SignInPage(),
        RegisterationPage().routeName: (context) => const RegisterationPage(),
        HomePage().routeName: (context) => const HomePage(),
      },
    );
  }
}
