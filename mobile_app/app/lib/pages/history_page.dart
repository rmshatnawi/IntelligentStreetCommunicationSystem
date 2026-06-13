// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/pages/history_page.dart
// Purpose:  Driver History & Tracking screen.
//           Reads the car's own movement history for the plate
//           registered in users/{uid}.
//
//   - Empty state -> link to OBU pairing if no plate.
//   - Last-seen card (most recent detection).
//   - Quick stats (today / segments).
//   - Map route-trace of recent detections.
//   - Timeline list of detections (vehicle_tracking).
//   - Stolen sightings panel (security_alerts) when reported.
//
//   Sources:
//     users/{uid}.plate_number
//     vehicle_tracking  where plate_number == plate  (by timestamp)
//     security_alerts   where plate_number == plate  (by generated_at)
//     GET /state        -> rsu_id -> lat/lng for the map trace
// ============================================================

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'package:app/app_theme.dart';
import 'package:app/widgets/custom_button.dart';
import 'package:app/pages/map_page.dart' show kBaseUrl;
import 'package:app/pages/obu_pairing_page.dart';

class _Detection {
  final String rsuId;
  final String segment;
  final double? speed;
  final bool isStolen;
  final DateTime time;
  const _Detection(
    this.rsuId,
    this.segment,
    this.speed,
    this.isStolen,
    this.time,
  );
}

class _Sighting {
  final String segment;
  final String rsuId;
  final double? speed;
  final DateTime time;
  const _Sighting(this.segment, this.rsuId, this.speed, this.time);
}

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});
  String get routeName => '/history';

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  final _db = FirebaseFirestore.instance;

  bool _loading = true;
  String _plate = '';
  String _plateStatus = 'none';
  List<_Detection> _detections = [];
  List<_Sighting> _sightings = [];
  final Map<String, LatLng> _rsuPos = {};
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  String? get _uid => FirebaseAuth.instance.currentUser?.uid;

  DateTime _parseTs(String? s) {
    if (s == null) return DateTime.now();
    final iso = s.endsWith('Z') ? s : '${s}Z';
    return DateTime.tryParse(iso)?.toLocal() ?? DateTime.now();
  }

  String _ago(DateTime t) {
    final d = DateTime.now().difference(t);
    if (d.inMinutes < 1) return 'just now';
    if (d.inMinutes < 60) return '${d.inMinutes}m ago';
    if (d.inHours < 24) return '${d.inHours}h ago';
    return '${d.inDays}d ago';
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    final uid = _uid;
    if (uid == null) {
      setState(() => _loading = false);
      return;
    }

    try {
      // 1. Plate from profile.
      final userDoc = await _db.collection('users').doc(uid).get();
      _plate = (userDoc.data()?['plate_number'] as String?) ?? '';
      _plateStatus = (userDoc.data()?['plate_status'] as String?) ?? 'none';

      if (_plate.isEmpty) {
        setState(() => _loading = false);
        return;
      }

      // 2. Movement history.
      final trackSnap = await _db
          .collection('vehicle_tracking')
          .where('plate_number', isEqualTo: _plate)
          .orderBy('timestamp', descending: true)
          .limit(50)
          .get();
      _detections = trackSnap.docs.map((d) {
        final m = d.data();
        return _Detection(
          (m['rsu_id'] as String?) ?? '',
          (m['segment'] as String?) ?? '',
          (m['speed'] as num?)?.toDouble(),
          (m['is_stolen'] as bool?) ?? false,
          _parseTs(m['timestamp'] as String?),
        );
      }).toList();

      // 3. Stolen sightings (only meaningful if reported).
      if (_plateStatus == 'stolen') {
        final alertSnap = await _db
            .collection('security_alerts')
            .where('plate_number', isEqualTo: _plate)
            .orderBy('generated_at', descending: true)
            .limit(20)
            .get();
        _sightings = alertSnap.docs.map((d) {
          final m = d.data();
          return _Sighting(
            (m['segment'] as String?) ?? '',
            (m['rsu_id'] as String?) ?? '',
            (m['speed'] as num?)?.toDouble(),
            _parseTs(m['generated_at'] as String?),
          );
        }).toList();
      } else {
        _sightings = [];
      }

      // 4. RSU coordinates for the map trace.
      await _loadRsuPositions();
    } catch (e) {
      _error = e.toString();
    }

    if (!mounted) return;
    setState(() => _loading = false);
  }

  Future<void> _loadRsuPositions() async {
    try {
      final res = await http
          .get(Uri.parse('$kBaseUrl/state'))
          .timeout(const Duration(seconds: 6));
      if (res.statusCode != 200) return;
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      for (final s in (body['segments'] as List?) ?? const []) {
        for (final r in (s['rsus'] as List?) ?? const []) {
          final id = r['rsu_id']?.toString();
          final lat = (r['lat'] as num?)?.toDouble();
          final lng = (r['lng'] as num?)?.toDouble();
          if (id != null && lat != null && lng != null) {
            _rsuPos[id] = LatLng(lat, lng);
          }
        }
      }
    } catch (_) {
      // Map trace is optional; ignore failures.
    }
  }

  // Chronological list of points that have known coordinates.
  List<LatLng> get _tracePoints {
    final chrono = _detections.reversed;
    final pts = <LatLng>[];
    for (final d in chrono) {
      final p = _rsuPos[d.rsuId];
      if (p != null) pts.add(p);
    }
    return pts;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('History & Tracking'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loading ? null : _load,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(onRefresh: _load, child: _body()),
    );
  }

  Widget _body() {
    if (_plate.isEmpty) return _emptyNoPlate();

    return ListView(
      padding: const EdgeInsets.all(AppTheme.space16),
      children: [
        if (_error != null) ...[
          Text(
            'Could not load everything: $_error',
            style: AppTheme.light.textTheme.bodySmall,
          ),
          const SizedBox(height: AppTheme.space12),
        ],
        _plateBar(),
        const SizedBox(height: AppTheme.space12),
        if (_detections.isEmpty)
          _emptyNoHistory()
        else ...[
          _lastSeenCard(),
          const SizedBox(height: AppTheme.space12),
          _statsRow(),
          const SizedBox(height: AppTheme.space16),
          if (_sightings.isNotEmpty) ...[
            _stolenPanel(),
            const SizedBox(height: AppTheme.space16),
          ],
          if (_tracePoints.isNotEmpty) ...[
            _sectionTitle('Route trace'),
            _mapTrace(),
            const SizedBox(height: AppTheme.space16),
          ],
          _sectionTitle('Timeline'),
          ..._detections.map(_timelineTile),
        ],
        const SizedBox(height: AppTheme.space24),
      ],
    );
  }

  Widget _plateBar() {
    final stolen = _plateStatus == 'stolen';
    final color = stolen ? AppTheme.congested : AppTheme.secondary;
    return Row(
      children: [
        Icon(Icons.directions_car, color: color),
        const SizedBox(width: AppTheme.space8),
        Text(_plate, style: AppTheme.light.textTheme.titleLarge),
        const Spacer(),
        if (stolen)
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppTheme.space8,
              vertical: AppTheme.space2,
            ),
            decoration: BoxDecoration(
              color: AppTheme.congested.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
            ),
            child: const Text(
              'STOLEN',
              style: TextStyle(
                color: AppTheme.congested,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
      ],
    );
  }

  Widget _lastSeenCard() {
    final d = _detections.first;
    final text = AppTheme.light.textTheme;
    return Material(
      color: AppTheme.secondary,
      borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.space16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Last seen',
              style: text.bodySmall?.copyWith(color: Colors.white70),
            ),
            const SizedBox(height: AppTheme.space4),
            Text(
              d.segment.isEmpty ? d.rsuId : d.segment,
              style: text.titleLarge?.copyWith(color: Colors.white),
            ),
            const SizedBox(height: AppTheme.space4),
            Text(
              '${d.rsuId} · ${_ago(d.time)}'
              '${d.speed != null ? ' · ${d.speed!.toStringAsFixed(0)} km/h' : ''}',
              style: text.bodyMedium?.copyWith(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statsRow() {
    final now = DateTime.now();
    final today = _detections
        .where(
          (d) =>
              d.time.year == now.year &&
              d.time.month == now.month &&
              d.time.day == now.day,
        )
        .length;
    final segments = _detections.map((d) => d.segment).toSet().length;
    return Row(
      children: [
        _stat('$today', 'today'),
        const SizedBox(width: AppTheme.space12),
        _stat('$segments', 'segments'),
        const SizedBox(width: AppTheme.space12),
        _stat('${_detections.length}', 'recent'),
      ],
    );
  }

  Widget _stat(String value, String label) {
    final text = AppTheme.light.textTheme;
    return Expanded(
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        elevation: AppTheme.elevationSmall,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: AppTheme.space12),
          child: Column(
            children: [
              Text(value, style: text.displayMedium),
              Text(
                label,
                style: text.bodySmall?.copyWith(color: AppTheme.textSecondary),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stolenPanel() {
    return Material(
      color: AppTheme.congested.withValues(alpha: 0.10),
      borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.space16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.warning_amber, color: AppTheme.congested),
                SizedBox(width: AppTheme.space8),
                Text(
                  'Stolen-vehicle sightings',
                  style: TextStyle(
                    color: AppTheme.congested,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.space8),
            ..._sightings.map(
              (s) => Padding(
                padding: const EdgeInsets.symmetric(vertical: AppTheme.space4),
                child: Text(
                  '${s.segment.isEmpty ? s.rsuId : s.segment} · ${s.rsuId} · ${_ago(s.time)}',
                  style: AppTheme.light.textTheme.bodyMedium,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _mapTrace() {
    final pts = _tracePoints;
    final last = pts.last;
    final first = pts.first;
    return SizedBox(
      height: 220,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        child: GoogleMap(
          initialCameraPosition: CameraPosition(target: last, zoom: 14),
          liteModeEnabled: true,
          markers: {
            Marker(
              markerId: const MarkerId('start'),
              position: first,
              icon: BitmapDescriptor.defaultMarkerWithHue(
                BitmapDescriptor.hueGreen,
              ),
              infoWindow: const InfoWindow(title: 'Earliest'),
            ),
            Marker(
              markerId: const MarkerId('last'),
              position: last,
              infoWindow: const InfoWindow(title: 'Last seen'),
            ),
          },
          polylines: {
            Polyline(
              polylineId: const PolylineId('trace'),
              points: pts,
              color: AppTheme.secondary,
              width: 5,
            ),
          },
        ),
      ),
    );
  }

  Widget _timelineTile(_Detection d) {
    final text = AppTheme.light.textTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppTheme.space4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 4, right: AppTheme.space12),
            child: Icon(
              d.isStolen ? Icons.circle : Icons.circle_outlined,
              size: 12,
              color: d.isStolen ? AppTheme.congested : AppTheme.secondary,
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  d.segment.isEmpty ? d.rsuId : d.segment,
                  style: text.titleMedium,
                ),
                Text(
                  '${d.rsuId} · ${_ago(d.time)}'
                  '${d.speed != null ? ' · ${d.speed!.toStringAsFixed(0)} km/h' : ''}',
                  style: text.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionTitle(String t) => Padding(
    padding: const EdgeInsets.only(bottom: AppTheme.space8),
    child: Text(t, style: AppTheme.light.textTheme.titleMedium),
  );

  Widget _emptyNoPlate() {
    return ListView(
      children: [
        const SizedBox(height: 120),
        Center(
          child: Padding(
            padding: const EdgeInsets.all(AppTheme.space24),
            child: Column(
              children: [
                const Icon(
                  Icons.directions_car_outlined,
                  size: 64,
                  color: AppTheme.textSecondary,
                ),
                const SizedBox(height: AppTheme.space16),
                Text(
                  'No vehicle registered',
                  style: AppTheme.light.textTheme.titleLarge,
                ),
                const SizedBox(height: AppTheme.space8),
                Text(
                  'Connect your OBU and register a plate to start tracking.',
                  textAlign: TextAlign.center,
                  style: AppTheme.light.textTheme.bodyMedium,
                ),
                const SizedBox(height: AppTheme.space16),
                CustomButton(
                  buttonText: 'Connect OBU',
                  onPressed: () async {
                    await Navigator.pushNamed(
                      context,
                      ObuPairingPage().routeName,
                    );
                    _load();
                  },
                  textStyle: AppTheme.light.textTheme.labelLarge!,
                  buttonColor: AppTheme.primary,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _emptyNoHistory() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 60),
      child: Center(
        child: Column(
          children: [
            const Icon(Icons.timeline, size: 56, color: AppTheme.textSecondary),
            const SizedBox(height: AppTheme.space12),
            Text(
              'No detections yet',
              style: AppTheme.light.textTheme.titleMedium,
            ),
            const SizedBox(height: AppTheme.space8),
            Text(
              'Your car has not passed an RSU yet.',
              textAlign: TextAlign.center,
              style: AppTheme.light.textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
