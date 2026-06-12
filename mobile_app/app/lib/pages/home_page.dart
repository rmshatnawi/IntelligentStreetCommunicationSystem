import 'package:app/pages/map_page.dart';
import 'package:app/pages/profile_page.dart';
import 'package:app/pages/settings_page.dart';
import 'package:app/app_theme.dart';
import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  String get routeName => '/home';

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  // Tab order: Profile(0), Settings(1), Map(2). Map is the default.
  static const int _mapIndex = 2;
  int _currentIndex = _mapIndex;

  // IndexedStack keeps all three pages mounted, so MapPage's polling
  // timer starts on home load and survives tab switches.
  final List<Widget> _pages = const [ProfilePage(), SettingsPage(), MapPage()];

  void _onTap(int index) {
    setState(() => _currentIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: IndexedStack(index: _currentIndex, children: _pages),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTap,
        type: BottomNavigationBarType.fixed,
        backgroundColor: AppTheme.secondary,
        selectedItemColor: AppTheme.primary,
        unselectedItemColor: Colors.white70,
        showUnselectedLabels: true,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profile',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            activeIcon: Icon(Icons.map),
            label: 'Map',
          ),
        ],
      ),
    );
  }
}
