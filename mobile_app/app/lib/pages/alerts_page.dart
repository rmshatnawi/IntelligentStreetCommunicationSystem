// TODO Implement this library.
// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/pages/alerts_page.dart
// Purpose:  Driver alerts screen.
//           Fetches GET /alerts and lists active traffic alerts,
//           colored by traffic state. Pull down or tap refresh
//           to reload. Reached from the map's top-left bell.
// ============================================================

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'package:app/app_theme.dart';
import 'package:app/pages/map_page.dart' show kBaseUrl;

class _Alert {
  final String message;
  final String segment;
  final String severity;
  final String trafficStatus;
  final String status;
  final double? avgSpeed;
  final String? generatedAt;

  const _Alert({
    required this.message,
    required this.segment,
    required this.severity,
    required this.trafficStatus,
    required this.status,
    required this.avgSpeed,
    required this.generatedAt,
  });
}

class AlertsPage extends StatefulWidget {
  const AlertsPage({super.key});
  String get routeName => '/alerts';

  @override
  State<AlertsPage> createState() => _AlertsPageState();
}

class _AlertsPageState extends State<AlertsPage> {
  List<_Alert> _alerts = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<String?> _idToken() async {
    return FirebaseAuth.instance.currentUser?.getIdToken();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final token = await _idToken();
      final res = await http
          .get(
            Uri.parse('$kBaseUrl/alerts'),
            headers: {
              'Content-Type': 'application/json',
              if (token != null) 'Authorization': 'Bearer $token',
            },
          )
          .timeout(const Duration(seconds: 6));

      if (res.statusCode != 200) {
        _fail('alerts HTTP ${res.statusCode}');
        return;
      }

      final body = jsonDecode(res.body) as Map<String, dynamic>;
      final list = (body['alerts'] as List?) ?? const [];

      final parsed = <_Alert>[];
      for (final a in list) {
        parsed.add(
          _Alert(
            message: a['alert_message']?.toString() ?? 'Traffic alert',
            segment: a['segment']?.toString() ?? '',
            severity: a['severity']?.toString() ?? '',
            trafficStatus: a['traffic_status']?.toString() ?? 'free',
            status: a['status']?.toString() ?? '',
            avgSpeed: (a['avg_speed'] as num?)?.toDouble(),
            generatedAt: a['generated_at']?.toString(),
          ),
        );
      }

      if (!mounted) return;
      setState(() {
        _alerts = parsed;
        _loading = false;
      });
    } catch (e) {
      _fail(e.toString());
    }
  }

  void _fail(String msg) {
    if (!mounted) return;
    setState(() {
      _error = msg;
      _loading = false;
    });
  }

  Color _stateColor(String status) {
    switch (status) {
      case 'severe':
        return AppTheme.congested;
      case 'congested':
        return Colors.deepOrange;
      case 'moderate':
        return AppTheme.moderate;
      default:
        return AppTheme.clear;
    }
  }

  String _ago(String? iso) {
    if (iso == null) return '';
    final t = DateTime.tryParse(iso.endsWith('Z') ? iso : '${iso}Z')?.toLocal();
    if (t == null) return '';
    final d = DateTime.now().difference(t);
    if (d.inMinutes < 1) return 'just now';
    if (d.inMinutes < 60) return '${d.inMinutes}m ago';
    if (d.inHours < 24) return '${d.inHours}h ago';
    return '${d.inDays}d ago';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Alerts'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loading ? null : _load,
          ),
        ],
      ),
      body: RefreshIndicator(onRefresh: _load, child: _body()),
    );
  }

  Widget _body() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return _Centered('Could not load alerts:\n$_error');
    }
    if (_alerts.isEmpty) {
      return const _Centered('No active alerts');
    }
    return ListView.separated(
      padding: const EdgeInsets.all(AppTheme.space16),
      itemCount: _alerts.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppTheme.space12),
      itemBuilder: (_, i) => _AlertCard(
        alert: _alerts[i],
        color: _stateColor(_alerts[i].trafficStatus),
        ago: _ago(_alerts[i].generatedAt),
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final _Alert alert;
  final Color color;
  final String ago;
  const _AlertCard({
    required this.alert,
    required this.color,
    required this.ago,
  });

  @override
  Widget build(BuildContext context) {
    final text = AppTheme.light.textTheme;
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      elevation: AppTheme.elevationSmall,
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              width: 6,
              decoration: BoxDecoration(
                color: color,
                borderRadius: const BorderRadius.horizontal(
                  left: Radius.circular(AppTheme.radiusMedium),
                ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.space16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            alert.segment.isEmpty ? 'Traffic' : alert.segment,
                            style: text.titleMedium,
                          ),
                        ),
                        if (ago.isNotEmpty) Text(ago, style: text.bodySmall),
                      ],
                    ),
                    const SizedBox(height: AppTheme.space4),
                    Text(alert.message, style: text.bodyMedium),
                    const SizedBox(height: AppTheme.space8),
                    Wrap(
                      spacing: AppTheme.space8,
                      runSpacing: AppTheme.space4,
                      children: [
                        _Chip(label: alert.trafficStatus, color: color),
                        if (alert.severity.isNotEmpty)
                          _Chip(
                            label: alert.severity,
                            color: AppTheme.secondary,
                          ),
                        if (alert.avgSpeed != null)
                          _Chip(
                            label: '${alert.avgSpeed!.toStringAsFixed(0)} km/h',
                            color: AppTheme.interactive,
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final Color color;
  const _Chip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.space8,
        vertical: AppTheme.space2,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _Centered extends StatelessWidget {
  final String text;
  const _Centered(this.text);

  @override
  Widget build(BuildContext context) {
    // ListView so RefreshIndicator still works when content is short.
    return ListView(
      children: [
        SizedBox(
          height: 400,
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(AppTheme.space24),
              child: Text(
                text,
                textAlign: TextAlign.center,
                style: AppTheme.light.textTheme.bodyLarge,
              ),
            ),
          ),
        ),
      ],
    );
  }
}
