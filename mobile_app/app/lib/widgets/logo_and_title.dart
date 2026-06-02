import 'package:flutter/material.dart';

class LogoAndTitle extends StatelessWidget {
  const LogoAndTitle(this.logoSize, this.titleStyle, {super.key});
  final double logoSize;
  final TextStyle titleStyle;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          height: logoSize,
          child: Image.asset('assets/images/dark_logo.png'),
        ),
        Text('Intelligent Street', style: titleStyle),
      ],
    );
  }
}
