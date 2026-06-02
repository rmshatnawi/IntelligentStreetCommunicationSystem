import 'package:app/widgets/custom_button.dart';
import 'package:app/widgets/logo_and_title.dart';
import 'package:flutter/material.dart';
import 'package:app/app_theme.dart';
import 'package:firebase_auth/firebase_auth.dart';

class RegisterationPage extends StatefulWidget {
  const RegisterationPage({super.key});
  String get routeName => '/register';

  @override
  State<RegisterationPage> createState() => _RegisterationPageState();
}

class _RegisterationPageState extends State<RegisterationPage> {
  final _auth = FirebaseAuth.instance;

  final usernameNode = FocusNode();
  final emailNode = FocusNode();
  final phoneNode = FocusNode();
  final passwordNode = FocusNode();
  final confirmNode = FocusNode();

  late String email;
  late String username;
  late String phone;
  late String password;
  late String confirmPassword;

  late List<Widget> fields;

  @override
  void initState() {
    super.initState();

    fields = [
      TextFormField(
        onChanged: (value) => username = value,
        focusNode: usernameNode,
        textInputAction: TextInputAction.next,
        onFieldSubmitted: (_) {
          FocusScope.of(context).requestFocus(emailNode);
        },
        decoration: const InputDecoration(hintText: 'Username'),
      ),

      TextFormField(
        onChanged: (value) => email = value,
        focusNode: emailNode,
        textInputAction: TextInputAction.next,
        onFieldSubmitted: (_) {
          FocusScope.of(context).requestFocus(phoneNode);
        },
        keyboardType: TextInputType.emailAddress,
        decoration: const InputDecoration(hintText: 'Email'),
      ),

      TextFormField(
        onChanged: (value) => phone = value,
        focusNode: phoneNode,
        textInputAction: TextInputAction.next,
        onFieldSubmitted: (_) {
          FocusScope.of(context).requestFocus(passwordNode);
        },
        keyboardType: TextInputType.phone,
        decoration: const InputDecoration(hintText: 'Phone Number'),
      ),

      TextFormField(
        onChanged: (value) => password = value,
        focusNode: passwordNode,
        textInputAction: TextInputAction.next,
        onFieldSubmitted: (_) {
          FocusScope.of(context).requestFocus(confirmNode);
        },
        obscureText: true,
        decoration: const InputDecoration(hintText: 'Password'),
      ),

      TextFormField(
        onChanged: (value) => confirmPassword = value,
        focusNode: confirmNode,
        textInputAction: TextInputAction.done,
        onFieldSubmitted: (_) {
          FocusScope.of(context).unfocus();
        },
        obscureText: true,
        decoration: const InputDecoration(hintText: 'Confirm Password'),
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      resizeToAvoidBottomInset: true,
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: AppTheme.space24),
        children: [
          const SizedBox(height: AppTheme.space64),

          LogoAndTitle(180, AppTheme.light.textTheme.titleLarge!),

          const SizedBox(height: AppTheme.space24),

          ..._buildFields(),

          const SizedBox(height: AppTheme.space24),

          CustomButton(
            buttonText: 'Register',
            onPressed: () async {
              try {
                final newUser = await _auth.createUserWithEmailAndPassword(
                  email: email,
                  password: password,
                );
                Navigator.pushNamed(context, '/home');
              } catch (e) {
                print(e);
              }
            },
            textStyle: AppTheme.light.textTheme.titleMedium!,
            buttonColor: AppTheme.primary,
          ),

          const SizedBox(height: 40),
        ],
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
