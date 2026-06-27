// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/pages/map_page.dart
// Purpose:  Driver map screen.
//           - Centers on the driver and follows movement (nav-style).
//           - Polls GET /state and draws road-state polylines only.
//           - Alerts button (top-left) routes to the alerts screen.
// ============================================================

import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'package:geolocator/geolocator.dart';
import 'package:app/app_theme.dart';

// -- WIRING POINT 1: SERVER URL ------------------------------
const String kBaseUrl = 'http://192.168.1.21:8000';

const Duration kPollInterval = Duration(seconds: 5);

// Used only until the first GPS fix arrives.
const LatLng kFallbackCenter = LatLng(32.0728, 36.0876);

const double kDriverZoom = 16;

// -- WIRING POINT 3: ALERTS ROUTE ----------------------------
const String kAlertsRoute = '/alerts';

class _Edge {
  final String status;
  final List<LatLng> path;
  const _Edge(this.status, this.path);
}

class MapPage extends StatefulWidget {
  const MapPage({super.key});
  String get routeName => '/map';

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  GoogleMapController? _controller;
  Timer? _timer;
  StreamSubscription<Position>? _posSub;

  List<_Edge> _edges = [];
  LatLng? _me;
  bool _locationReady = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initLocation();
    _refresh();
    _timer = Timer.periodic(kPollInterval, (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    _posSub?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  // ---- Location: permission, first fix, then a follow stream ----
  Future<void> _initLocation() async {
    try {
      final serviceOn = await Geolocator.isLocationServiceEnabled();
      if (!serviceOn) {
        _setError('Location services are off');
        return;
      }

      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.denied ||
          perm == LocationPermission.deniedForever) {
        _setError('Location permission denied');
        return;
      }

      // Permission granted: flip the flag so the map enables the blue dot.
      if (!mounted) return;
      setState(() => _locationReady = true);

      final first = await Geolocator.getCurrentPosition();
      _onPosition(first);

      _posSub = Geolocator.getPositionStream(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          distanceFilter: 5,
        ),
      ).listen(_onPosition);
    } catch (e) {
      _setError(e.toString());
    }
  }

  void _onPosition(Position pos) {
    final here = LatLng(pos.latitude, pos.longitude);
    if (!mounted) return;
    setState(() => _me = here);
    // Follow the driver, nav-style.
    _controller?.animateCamera(CameraUpdate.newLatLng(here));
  }

  void _recenter() {
    if (_me != null) {
      _controller?.animateCamera(CameraUpdate.newLatLngZoom(_me!, kDriverZoom));
    }
  }

  void _openAlerts() {
    Navigator.pushNamed(context, kAlertsRoute);
  }

  // -- WIRING POINT 2: AUTH TOKEN ----------------------------
  Future<String?> _idToken() async {
    return FirebaseAuth.instance.currentUser?.getIdToken();
  }

  List<LatLng> _parsePath(dynamic raw) {
    final out = <LatLng>[];
    for (final p in (raw as List?) ?? const []) {
      final lat = (p['lat'] as num?)?.toDouble();
      final lng = (p['lng'] as num?)?.toDouble();
      if (lat != null && lng != null) out.add(LatLng(lat, lng));
    }
    return out;
  }

  // Pull road-state edges from /state. RSU points are ignored on purpose.
  Future<void> _refresh() async {
    try {
      final token = await _idToken();
      final res = await http
          .get(
            Uri.parse('$kBaseUrl/state'),
            headers: {
              'Content-Type': 'application/json',
              if (token != null) 'Authorization': 'Bearer $token',
            },
          )
          .timeout(const Duration(seconds: 6));

      if (res.statusCode != 200) {
        _setError('state HTTP ${res.statusCode}');
        return;
      }

      final body = jsonDecode(res.body) as Map<String, dynamic>;
      final list = (body['segments'] as List?) ?? const [];

      final edges = <_Edge>[];
      for (final s in list) {
        for (final e in (s['edges'] as List?) ?? const []) {
          edges.add(
            _Edge(e['status']?.toString() ?? 'free', _parsePath(e['path'])),
          );
        }
      }

      if (!mounted) return;
      setState(() {
        _edges = edges;
        _error = null;
      });
    } catch (e) {
      _setError(e.toString());
    }
  }

  void _setError(String msg) {
    if (!mounted) return;
    setState(() => _error = msg);
  }

  Color _color(String status) {
    switch (status) {
      case 'severe':
        return AppTheme.congested; // red
      case 'congested':
        return Colors.deepOrange;
      case 'moderate':
        return AppTheme.moderate; // orange
      default:
        return AppTheme.clear; // green
    }
  }

  Set<Polyline> get _lines {
    final l = <Polyline>{};
    for (var i = 0; i < _edges.length; i++) {
      final e = _edges[i];
      if (e.path.length < 2) continue;
      l.add(
        Polyline(
          polylineId: PolylineId('edge_$i'),
          points: e.path,
          color: _color(e.status),
          width: 6,
        ),
      );
    }
    return l;
  }

  @override
  Widget build(BuildContext context) {
    final initial = _me ?? kFallbackCenter;
    return Scaffold(
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(
              target: initial,
              zoom: kDriverZoom,
            ),
            polylines: _lines,
            myLocationEnabled: _locationReady,
            myLocationButtonEnabled: false,
            zoomControlsEnabled: false,
            mapToolbarEnabled: false,
            onMapCreated: (c) {
              _controller = c;
              if (_me != null) {
                c.moveCamera(CameraUpdate.newLatLngZoom(_me!, kDriverZoom));
              }
            },
          ),

          // Alerts button - top-left.
          SafeArea(
            child: Align(
              alignment: Alignment.topLeft,
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.space12),
                child: _RoundIcon(
                  icon: Icons.notifications_outlined,
                  onTap: _openAlerts,
                ),
              ),
            ),
          ),

          // Recenter button - bottom-right.
          SafeArea(
            child: Align(
              alignment: Alignment.bottomRight,
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.space12),
                child: _RoundIcon(icon: Icons.my_location, onTap: _recenter),
              ),
            ),
          ),

          // Road-state legend - bottom-left.
          const SafeArea(
            child: Align(
              alignment: Alignment.bottomLeft,
              child: Padding(
                padding: EdgeInsets.all(AppTheme.space12),
                child: _Legend(),
              ),
            ),
          ),

          if (_error != null)
            SafeArea(
              child: Align(
                alignment: Alignment.topCenter,
                child: Padding(
                  padding: const EdgeInsets.all(AppTheme.space12),
                  child: _Banner('No live data: $_error'),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _RoundIcon extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _RoundIcon({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppTheme.secondary,
      shape: const CircleBorder(),
      elevation: AppTheme.elevationMedium,
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(AppTheme.space12),
          child: Icon(icon, color: Colors.white),
        ),
      ),
    );
  }
}

class _Legend extends StatelessWidget {
  const _Legend();

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      elevation: AppTheme.elevationSmall,
      child: const Padding(
        padding: EdgeInsets.symmetric(
          horizontal: AppTheme.space12,
          vertical: AppTheme.space8,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _LegendRow(AppTheme.clear, 'Clear'),
            SizedBox(height: AppTheme.space4),
            _LegendRow(AppTheme.moderate, 'Moderate'),
            SizedBox(height: AppTheme.space4),
            _LegendRow(Colors.deepOrange, 'Congested'),
            SizedBox(height: AppTheme.space4),
            _LegendRow(AppTheme.congested, 'Severe'),
          ],
        ),
      ),
    );
  }
}

class _LegendRow extends StatelessWidget {
  final Color color;
  final String label;
  const _LegendRow(this.color, this.label);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 16, height: 4, color: color),
        const SizedBox(width: AppTheme.space8),
        Text(label, style: AppTheme.light.textTheme.bodySmall),
      ],
    );
  }
}

class _Banner extends StatelessWidget {
  final String text;
  const _Banner(this.text);

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black87,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Text(
          text,
          style: const TextStyle(color: Colors.white, fontSize: 12),
        ),
      ),
    );
  }
}
