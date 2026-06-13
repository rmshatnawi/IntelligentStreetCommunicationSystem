// TODO Implement this library.
// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/services/obu_service.dart
// Purpose:  Abstraction over the On-Board Unit (OBU) connection.
//           Two implementations behind one interface:
//             - MockObuService : simulator, no hardware needed (demo).
//             - BleObuService  : real ESP32 over BLE (flutter_blue_plus).
//           The app SENDS the plate number to the OBU after connecting.
//
//  IMPORTANT: kObuServiceUuid / kObuPlateCharUuid MUST match the
//  UUIDs declared in the ESP32 firmware. These are the common ESP32
//  BLE example UUIDs — change them in both places together.
// ============================================================

import 'dart:async';
import 'dart:convert';

import 'package:flutter_blue_plus/flutter_blue_plus.dart';

const String kObuServiceUuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b';
const String kObuPlateCharUuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8';

/// A discovered OBU candidate. [bleDevice] is null for the simulator.
class ObuDevice {
  final String id;
  final String name;
  final BluetoothDevice? bleDevice;
  const ObuDevice(this.id, this.name, this.bleDevice);
}

abstract class ObuService {
  Future<List<ObuDevice>> scan({Duration timeout});
  Future<void> connect(ObuDevice device);
  Future<void> sendPlate(String plate);
  Future<void> disconnect();
}

// ---- Simulator: works with no hardware ----
class MockObuService implements ObuService {
  @override
  Future<List<ObuDevice>> scan({
    Duration timeout = const Duration(seconds: 2),
  }) async {
    await Future.delayed(const Duration(seconds: 1));
    return const [ObuDevice('MOCK-OBU-0001', 'ISCS-OBU (simulator)', null)];
  }

  @override
  Future<void> connect(ObuDevice device) async {
    await Future.delayed(const Duration(milliseconds: 800));
  }

  @override
  Future<void> sendPlate(String plate) async {
    await Future.delayed(const Duration(milliseconds: 600));
  }

  @override
  Future<void> disconnect() async {}
}

// ---- Real ESP32 over BLE ----
class BleObuService implements ObuService {
  BluetoothDevice? _device;
  BluetoothCharacteristic? _plateChar;

  @override
  Future<List<ObuDevice>> scan({
    Duration timeout = const Duration(seconds: 6),
  }) async {
    final found = <String, ObuDevice>{};

    final sub = FlutterBluePlus.scanResults.listen((results) {
      for (final r in results) {
        final name = r.device.platformName;
        found[r.device.remoteId.str] = ObuDevice(
          r.device.remoteId.str,
          name.isEmpty ? '(unnamed device)' : name,
          r.device,
        );
      }
    });

    // No service filter: ESP32 firmware may not advertise the service.
    // Show everything and let the user pick the OBU by name.
    await FlutterBluePlus.startScan(timeout: timeout);
    await Future.delayed(timeout);
    await FlutterBluePlus.stopScan();
    await sub.cancel();

    return found.values.toList();
  }

  @override
  Future<void> connect(ObuDevice device) async {
    final dev = device.bleDevice;
    if (dev == null) throw Exception('No BLE device attached');

    await dev.connect(
      timeout: const Duration(seconds: 12),
      license: License.nonprofit,
    );
    final services = await dev.discoverServices();

    for (final s in services) {
      if (s.uuid == Guid(kObuServiceUuid)) {
        for (final c in s.characteristics) {
          if (c.uuid == Guid(kObuPlateCharUuid)) {
            _plateChar = c;
          }
        }
      }
    }

    _device = dev;
    if (_plateChar == null) {
      throw Exception(
        'Connected, but the OBU plate service was not found. '
        'Check the firmware UUIDs.',
      );
    }
  }

  @override
  Future<void> sendPlate(String plate) async {
    final c = _plateChar;
    if (c == null) throw Exception('Not connected to an OBU');
    await c.write(utf8.encode(plate), withoutResponse: false);
  }

  @override
  Future<void> disconnect() async {
    try {
      await _device?.disconnect();
    } catch (_) {}
    _device = null;
    _plateChar = null;
  }
}
