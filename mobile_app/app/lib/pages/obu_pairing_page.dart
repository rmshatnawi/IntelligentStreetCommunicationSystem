// TODO Implement this library.
// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/pages/obu_pairing_page.dart
// Purpose:  OBU pairing + plate registration flow.
//           1. Scan (real BLE) or use the simulator.
//           2. Connect to the OBU.
//           3. Enter the plate; app sends it to the OBU over BLE.
//           4. Bind plate <-> OBU <-> user in Firestore.
//
//  Firestore writes on success:
//    users/{uid}   { plate_number, plate_status:'active',
//                    obu_id, obu_name, updated_at }
//    obus/{obu_id} { plate_number, owner_uid, updated_at }
//
//  Returns true via Navigator.pop when registration succeeds.
// ============================================================

import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:app/app_theme.dart';
import 'package:app/widgets/custom_button.dart';
import 'package:app/services/obu_service.dart';

class ObuPairingPage extends StatefulWidget {
  const ObuPairingPage({super.key});
  String get routeName => '/obu';

  @override
  State<ObuPairingPage> createState() => _ObuPairingPageState();
}

class _ObuPairingPageState extends State<ObuPairingPage> {
  final _db = FirebaseFirestore.instance;
  final _plateC = TextEditingController();

  bool _useSimulator = true; // OBU not on hand -> simulator by default
  ObuService _svc = MockObuService();

  bool _scanning = false;
  bool _connecting = false;
  bool _sending = false;

  List<ObuDevice> _devices = [];
  ObuDevice? _connected;

  @override
  void dispose() {
    _svc.disconnect();
    _plateC.dispose();
    super.dispose();
  }

  void _snack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  void _setMode(bool sim) {
    _svc.disconnect();
    setState(() {
      _useSimulator = sim;
      _svc = sim ? MockObuService() : BleObuService();
      _devices = [];
      _connected = null;
    });
  }

  Future<void> _scan() async {
    setState(() {
      _scanning = true;
      _devices = [];
      _connected = null;
    });
    try {
      final found = await _svc.scan();
      if (!mounted) return;
      setState(() => _devices = found);
      if (found.isEmpty) _snack('No devices found');
    } catch (e) {
      _snack('Scan failed: $e');
    } finally {
      if (mounted) setState(() => _scanning = false);
    }
  }

  Future<void> _connect(ObuDevice d) async {
    setState(() => _connecting = true);
    try {
      await _svc.connect(d);
      if (!mounted) return;
      setState(() => _connected = d);
      _snack('Connected to ${d.name}');
    } catch (e) {
      _snack('Connect failed: $e');
    } finally {
      if (mounted) setState(() => _connecting = false);
    }
  }

  Future<void> _sendAndRegister() async {
    final uid = FirebaseAuth.instance.currentUser?.uid;
    final obu = _connected;
    final plate = _plateC.text.trim();
    if (uid == null || obu == null) return;
    if (plate.isEmpty) {
      _snack('Enter a plate number');
      return;
    }

    setState(() => _sending = true);
    try {
      // 1. Push the plate to the OBU over BLE.
      await _svc.sendPlate(plate);

      // 2. Bind everything in Firestore.
      await _db.collection('users').doc(uid).set({
        'plate_number': plate,
        'plate_status': 'active',
        'obu_id': obu.id,
        'obu_name': obu.name,
        'updated_at': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));

      await _db.collection('obus').doc(obu.id).set({
        'plate_number': plate,
        'owner_uid': uid,
        'updated_at': FieldValue.serverTimestamp(),
      });

      if (!mounted) return;
      _snack('Plate registered to OBU');
      Navigator.pop(context, true);
    } catch (e) {
      _snack('Could not register: $e');
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Connect OBU')),
      body: ListView(
        padding: const EdgeInsets.all(AppTheme.space24),
        children: [
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Use simulator (no device needed)'),
            value: _useSimulator,
            activeColor: AppTheme.primary,
            onChanged: (v) => _setMode(v),
          ),
          const Divider(),

          if (_connected == null) ..._connectStep() else ..._plateStep(),
        ],
      ),
    );
  }

  List<Widget> _connectStep() {
    return [
      const SizedBox(height: AppTheme.space8),
      Text(
        'Step 1 — find your OBU',
        style: AppTheme.light.textTheme.titleMedium,
      ),
      const SizedBox(height: AppTheme.space12),
      CustomButton(
        buttonText: _scanning ? 'Scanning...' : 'Scan for OBU',
        onPressed: (_scanning || _connecting) ? () {} : _scan,
        textStyle: AppTheme.light.textTheme.labelLarge!,
        buttonColor: AppTheme.primary,
      ),
      const SizedBox(height: AppTheme.space12),
      if (_scanning) const Center(child: CircularProgressIndicator()),
      ..._devices.map(
        (d) => Card(
          color: Colors.white,
          child: ListTile(
            leading: const Icon(Icons.memory, color: AppTheme.secondary),
            title: Text(d.name),
            subtitle: Text(d.id),
            trailing: _connecting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.chevron_right),
            onTap: _connecting ? null : () => _connect(d),
          ),
        ),
      ),
    ];
  }

  List<Widget> _plateStep() {
    return [
      const SizedBox(height: AppTheme.space8),
      Row(
        children: [
          const Icon(Icons.check_circle, color: AppTheme.clear),
          const SizedBox(width: AppTheme.space8),
          Expanded(
            child: Text(
              'Connected to ${_connected!.name}',
              style: AppTheme.light.textTheme.bodyLarge,
            ),
          ),
        ],
      ),
      const SizedBox(height: AppTheme.space16),
      Text(
        'Step 2 — enter your plate',
        style: AppTheme.light.textTheme.titleMedium,
      ),
      const SizedBox(height: AppTheme.space12),
      TextFormField(
        controller: _plateC,
        textCapitalization: TextCapitalization.characters,
        decoration: const InputDecoration(
          hintText: 'Plate number (e.g. 12-34567)',
        ),
      ),
      CustomButton(
        buttonText: _sending ? 'Sending...' : 'Send to OBU & register',
        onPressed: _sending ? () {} : _sendAndRegister,
        textStyle: AppTheme.light.textTheme.labelLarge!,
        buttonColor: AppTheme.primary,
      ),
      TextButton(
        onPressed: _sending
            ? null
            : () {
                _svc.disconnect();
                setState(() => _connected = null);
              },
        child: const Text('Disconnect'),
      ),
    ];
  }
}
