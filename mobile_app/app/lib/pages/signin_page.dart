import 'package:app/pages/map_page.dart';
import 'package:app/widgets/custom_button.dart';
import 'package:app/widgets/logo_and_title.dart';
import 'package:flutter/material.dart';
import 'package:app/app_theme.dart';

class SignInPage extends StatefulWidget {
  const SignInPage({super.key});
  String get routeName => '/signin';

  @override
  State<SignInPage> createState() => SignInPageState();
}

class SignInPageState extends State<SignInPage> {
  final emailNode = FocusNode();
  final passwordNode = FocusNode();

  late List<Widget> fields;

  @override
  void initState() {
    super.initState();

    fields = [
      TextFormField(
        focusNode: emailNode,
        textInputAction: TextInputAction.next,
        onFieldSubmitted: (_) {
          FocusScope.of(context).requestFocus(passwordNode);
        },
        keyboardType: TextInputType.emailAddress,
        decoration: const InputDecoration(hintText: 'Email'),
      ),

      TextFormField(
        focusNode: passwordNode,
        textInputAction: TextInputAction.done,
        onFieldSubmitted: (_) {
          FocusScope.of(context).unfocus();
        },
        obscureText: true,
        decoration: const InputDecoration(hintText: 'Password'),
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      resizeToAvoidBottomInset: true,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: AppTheme.space24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            LogoAndTitle(180, AppTheme.light.textTheme.titleLarge!),

            const SizedBox(height: AppTheme.space24),

            ..._buildFields(),

            const SizedBox(height: AppTheme.space24),

            CustomButton(
              buttonText: 'Sign In',
              onPressed: () {
                Navigator.pushNamed(context, MapPage().routeName);
              },
              textStyle: AppTheme.light.textTheme.titleMedium!,
              buttonColor: AppTheme.primary,
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildFields() {
    const gap = SizedBox(height: AppTheme.space12);

    final result = <Widget>[];
    for (int i = 0; i < fields.length; i++) {
      result.add(fields[i]);
      if (i != fields.length - 1) {
        result.add(gap);
      }
    }
    return result;
  }
}
