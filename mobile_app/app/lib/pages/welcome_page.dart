import 'package:app/pages/Registeration.dart';
import 'package:app/pages/signin_page.dart';
import 'package:app/widgets/custom_button.dart';
import 'package:app/widgets/logo_and_title.dart';
import 'package:flutter/material.dart';
import 'package:app/app_theme.dart';

class WelcomePage extends StatefulWidget {
  const WelcomePage({super.key});
  String get routeName => '/welcome';

  @override
  State<WelcomePage> createState() => _WelcomePageState();
}

class _WelcomePageState extends State<WelcomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: AppTheme.space24),
        child: SafeArea(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              LogoAndTitle(180, AppTheme.light.textTheme.titleLarge!),
              SizedBox(height: AppTheme.space24),
              CustomButton(
                buttonText: 'Sign In',
                onPressed: () {
                  Navigator.pushNamed(context, SignInPage().routeName);
                },
                textStyle: AppTheme.light.textTheme.labelLarge!,
                buttonColor: AppTheme.primary,
              ),
              CustomButton(
                buttonText: 'Register',
                onPressed: () {
                  Navigator.pushNamed(context, RegisterationPage().routeName);
                },
                textStyle: AppTheme.light.textTheme.labelLarge!,
                buttonColor: AppTheme.secondary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
