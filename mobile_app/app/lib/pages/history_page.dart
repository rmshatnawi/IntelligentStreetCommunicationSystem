import 'package:app/app_theme.dart';
import 'package:flutter/material.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});
  String get routeName => '/history';

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('History & Tracking')),
      body: Center(
        child: Text(
          'History & Tracking',
          style: AppTheme.light.textTheme.titleLarge,
        ),
      ),
    );
  }
}
