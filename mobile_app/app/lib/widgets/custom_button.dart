import 'package:app/app_theme.dart';
import 'package:flutter/material.dart';

class CustomButton extends StatelessWidget {
  const CustomButton({
    super.key,
    required this.buttonText,
    required this.onPressed,
    required this.textStyle,
    required this.buttonColor,
  });

  final String buttonText;
  final VoidCallback onPressed;
  final TextStyle textStyle;
  final Color buttonColor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppTheme.space12),
      child: Material(
        elevation: AppTheme.elevationMedium,
        color: buttonColor,
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        child: MaterialButton(
          onPressed: onPressed,
          minWidth: double.infinity,
          height: 50,
          child: Text(buttonText, style: textStyle),
        ),
      ),
    );
  }
}
