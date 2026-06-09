// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/pages/map_page.dart
// Purpose:  Driver map screen.
//           Polls GET /state. The server is the source of truth:
//           it returns each segment's traffic status and the RSU
//           points on it. The app draws a marker per RSU and a
//           colored line per segment.
//
// Color:  free=green  moderate=amber  congested=orange  severe=red
// ============================================================

import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

// -- WIRING POINT 1: SERVER URL ------------------------------
const String kBaseUrl = 'http://192.168.1.21:8000';

const Duration kPollInterval = Duration(seconds: 30);

// Fallback map center used before any signal arrives .
const LatLng kFallbackCenter = LatLng(32.50376051952631, 35.933664952564776);

class _Seg {
  final String segment;
  final String status; // free | moderate | congested | severe
  final List<LatLng> points; // RSU positions (markers)
  final List<LatLng> path; // road-following shape from the server
  const _Seg(this.segment, this.status, this.points, this.path);
}

class MapPage extends StatefulWidget {
  const MapPage({super.key});

  final String routeName = '/map';

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  GoogleMapController? _controller;
  Timer? _timer;
  List<_Seg> _segments = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
    _timer = Timer.periodic(kPollInterval, (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  // -- WIRING POINT 2: AUTH TOKEN ----------------------------
  Future<String?> _idToken() async {
    return FirebaseAuth.instance.currentUser?.getIdToken();
  }

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
        setState(() => _error = 'state HTTP ${res.statusCode}');
        return;
      }

      final body = jsonDecode(res.body) as Map<String, dynamic>;
      final list = (body['segments'] as List?) ?? const [];

      final parsed = <_Seg>[];
      for (final s in list) {
        final seg = s['segment']?.toString() ?? '';
        final status = s['status']?.toString() ?? 'free';

        final rsus = (s['rsus'] as List?) ?? const [];
        final pts = <LatLng>[];
        for (final r in rsus) {
          final lat = (r['lat'] as num?)?.toDouble();
          final lng = (r['lng'] as num?)?.toDouble();
          if (lat != null && lng != null) pts.add(LatLng(lat, lng));
        }
        pts.sort((a, b) => a.longitude.compareTo(b.longitude));

        final rawPath = (s['path'] as List?) ?? const [];
        final path = <LatLng>[];
        for (final p in rawPath) {
          final lat = (p['lat'] as num?)?.toDouble();
          final lng = (p['lng'] as num?)?.toDouble();
          if (lat != null && lng != null) path.add(LatLng(lat, lng));
        }

        parsed.add(_Seg(seg, status, pts, path));
      }

      if (!mounted) return;
      setState(() {
        _segments = parsed;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  double _hue(String status) {
    switch (status) {
      case 'severe':
        return BitmapDescriptor.hueRed;
      case 'congested':
        return BitmapDescriptor.hueOrange;
      case 'moderate':
        return BitmapDescriptor.hueYellow;
      default:
        return BitmapDescriptor.hueGreen; // free
    }
  }

  Color _color(String status) {
    switch (status) {
      case 'severe':
        return Colors.red;
      case 'congested':
        return Colors.orange;
      case 'moderate':
        return Colors.amber;
      default:
        return Colors.green; // free
    }
  }

  String _label(String status) {
    switch (status) {
      case 'severe':
        return 'Severe congestion';
      case 'congested':
        return 'Congested';
      case 'moderate':
        return 'Moderate';
      default:
        return 'Clear';
    }
  }

  Set<Marker> get _markers {
    final m = <Marker>{};
    for (final seg in _segments) {
      for (var i = 0; i < seg.points.length; i++) {
        final p = seg.points[i];
        m.add(
          Marker(
            markerId: MarkerId('${seg.segment}_$i'),
            position: p,
            icon: BitmapDescriptor.defaultMarkerWithHue(_hue(seg.status)),
            infoWindow: InfoWindow(
              title: seg.segment,
              snippet: _label(seg.status),
            ),
          ),
        );
      }
    }
    return m;
  }

  Set<Polyline> get _lines {
    final l = <Polyline>{};
    for (final seg in _segments) {
      // Prefer the server's road-following shape; fall back to the two
      // RSU points (straight line) if the server returned no path.
      final shape = seg.path.length >= 2 ? seg.path : seg.points;
      if (shape.length < 2) continue;
      l.add(
        Polyline(
          polylineId: PolylineId(seg.segment),
          points: shape,
          color: _color(seg.status),
          width: 6,
        ),
      );
    }
    return l;
  }

  LatLng get _center {
    final all = _segments.expand((s) => s.points).toList();
    if (all.isEmpty) return kFallbackCenter;
    final lat = all.map((p) => p.latitude).reduce((a, b) => a + b) / all.length;
    final lng =
        all.map((p) => p.longitude).reduce((a, b) => a + b) / all.length;
    return LatLng(lat, lng);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Live RSU Map')),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(target: _center, zoom: 14.5),
            markers: _markers,
            polylines: _lines,
            myLocationButtonEnabled: false,
            onMapCreated: (c) => _controller = c,
          ),
          if (_segments.isEmpty && _error == null)
            const Positioned(
              left: 12,
              right: 12,
              bottom: 12,
              child: _Banner('Waiting for RSU signals...'),
            ),
          if (_error != null)
            Positioned(
              left: 12,
              right: 12,
              bottom: 12,
              child: _Banner('No live data: $_error'),
            ),
        ],
      ),
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
