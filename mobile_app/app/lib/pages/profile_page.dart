// ============================================================
// Project:  Intelligent Street Communication System (ISCS)
// File:     lib/pages/profile_page.dart
// Purpose:  Driver profile screen.
//           - View mode by default; Edit reveals input boxes.
//           - Name + phone persist to Firestore users/{uid}.
//           - Email change (verification link), change/reset password.
//           - Vehicle: register the plate by connecting the OBU
//             (BLE) on a dedicated page; report/recover stolen here.
//           - Sign out.
// ============================================================

import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:app/app_theme.dart';
import 'package:app/widgets/custom_button.dart';
import 'package:app/pages/obu_pairing_page.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});
  String get routeName => '/profile';

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final _auth = FirebaseAuth.instance;
  final _db = FirebaseFirestore.instance;

  final _nameC = TextEditingController();
  final _phoneC = TextEditingController();
  final _emailC = TextEditingController();

  bool _loading = true;
  bool _saving = false;
  bool _editing = false;
  String _plate = '';
  String _plateStatus = 'none'; // none | active | stolen
  String _role = '';

  User? get _user => _auth.currentUser;
  String? get _uid => _user?.uid;

  @override
  void initState() {
    super.initState();
    _load(showSpinner: true);
  }

  @override
  void dispose() {
    _nameC.dispose();
    _phoneC.dispose();
    _emailC.dispose();
    super.dispose();
  }

  Future<void> _load({bool showSpinner = false}) async {
    if (showSpinner && mounted) setState(() => _loading = true);

    final uid = _uid;
    _emailC.text = _user?.email ?? '';
    var name = _user?.displayName ?? '';
    var phone = '';
    var plate = '';
    var plateStatus = 'none';

    try {
      final res = await _user?.getIdTokenResult();
      _role = (res?.claims?['role'] as String?) ?? 'none';
    } catch (_) {
      _role = 'none';
    }

    if (uid != null) {
      try {
        final doc = await _db.collection('users').doc(uid).get();
        final data = doc.data();
        if (data != null) {
          name = (data['name'] as String?) ?? name;
          phone = (data['phone'] as String?) ?? '';
          plate = (data['plate_number'] as String?) ?? '';
          plateStatus = (data['plate_status'] as String?) ?? 'none';
        }
      } catch (e) {
        _snack('Could not load profile: $e');
      }
    }

    _nameC.text = name;
    _phoneC.text = phone;
    _plate = plate;
    _plateStatus = plateStatus;

    if (!mounted) return;
    setState(() => _loading = false);
  }

  void _snack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  Future<void> _saveProfile() async {
    final uid = _uid;
    if (uid == null) return;
    setState(() => _saving = true);
    try {
      await _db.collection('users').doc(uid).set({
        'name': _nameC.text.trim(),
        'phone': _phoneC.text.trim(),
        'email': _user?.email ?? '',
        'updated_at': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));

      try {
        await _user?.updateDisplayName(_nameC.text.trim());
        await _user?.reload();
      } catch (_) {}

      final newEmail = _emailC.text.trim();
      if (newEmail.isNotEmpty && newEmail != _user?.email) {
        try {
          await _user?.verifyBeforeUpdateEmail(newEmail);
          _snack('Verification link sent to $newEmail. Confirm it to apply.');
        } on FirebaseAuthException catch (e) {
          if (e.code == 'requires-recent-login') {
            _snack('Email needs re-login. Sign out and in, then retry.');
          } else {
            _snack('Email update failed: ${e.message}');
          }
        }
      } else {
        _snack('Profile saved');
      }

      await _load();
      if (mounted) setState(() => _editing = false);
    } catch (e) {
      _snack('Could not save: $e');
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  void _cancelEdit() {
    setState(() => _editing = false);
    _load();
  }

  Future<void> _changePassword() async {
    final newC = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Change password'),
        content: TextField(
          controller: newC,
          obscureText: true,
          decoration: const InputDecoration(hintText: 'New password'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Update'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    final pw = newC.text.trim();
    if (pw.length < 6) {
      _snack('Password must be at least 6 characters');
      return;
    }
    try {
      await _user?.updatePassword(pw);
      _snack('Password updated');
    } on FirebaseAuthException catch (e) {
      if (e.code == 'requires-recent-login') {
        _snack('Please sign out and sign in again, then retry.');
      } else {
        _snack('Password change failed: ${e.message}');
      }
    }
  }

  Future<void> _resetPassword() async {
    final email = _user?.email;
    if (email == null) return;
    try {
      await _auth.sendPasswordResetEmail(email: email);
      _snack('Reset link sent to $email');
    } catch (e) {
      _snack('Could not send reset: $e');
    }
  }

  Future<void> _openObu() async {
    final result = await Navigator.pushNamed(
      context,
      ObuPairingPage().routeName,
    );
    if (result == true) await _load();
  }

  Future<void> _reportStolen() async {
    final uid = _uid;
    if (uid == null || _plate.isEmpty) {
      _snack('Register a vehicle first');
      return;
    }
    try {
      await _db.collection('stolen_vehicles').doc(uid).set({
        'plate_number': _plate,
        'vehicle_id': uid,
        'owner_uid': uid,
        'status': 'active',
        'reported_at': FieldValue.serverTimestamp(),
      });
      await _db.collection('users').doc(uid).set({
        'plate_status': 'stolen',
      }, SetOptions(merge: true));
      setState(() => _plateStatus = 'stolen');
      _snack('Reported stolen. RSUs will flag this plate.');
    } catch (e) {
      _snack('Could not report: $e');
    }
  }

  Future<void> _markRecovered() async {
    final uid = _uid;
    if (uid == null) return;
    try {
      await _db.collection('stolen_vehicles').doc(uid).delete();
      await _db.collection('users').doc(uid).set({
        'plate_status': 'active',
      }, SetOptions(merge: true));
      setState(() => _plateStatus = 'active');
      _snack('Marked as recovered');
    } catch (e) {
      _snack('Could not update: $e');
    }
  }

  Future<void> _signOut() async {
    await _auth.signOut();
    if (!mounted) return;
    Navigator.of(context).pushNamedAndRemoveUntil('/welcome', (r) => false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Reload',
            onPressed: _loading ? null : () => _load(showSpinner: true),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sign out',
            onPressed: _signOut,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(AppTheme.space24),
              children: [
                _header(),
                const SizedBox(height: AppTheme.space24),

                _sectionTitle('Account'),
                if (_editing) _editAccount() else _viewAccount(),

                // const SizedBox(height: AppTheme.space16),
                // _sectionTitle('Security'),
                // OutlinedButton(
                //   onPressed: _changePassword,
                //   child: const Text('Change password'),
                // ),
                // const SizedBox(height: AppTheme.space8),
                // OutlinedButton(
                //   onPressed: _resetPassword,
                //   child: const Text('Send password reset email'),
                // ),
                const SizedBox(height: AppTheme.space16),
                _sectionTitle('My vehicle (optional)'),
                _vehicleSection(),

                const SizedBox(height: AppTheme.space32),
              ],
            ),
    );
  }

  Widget _vehicleSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _plateStatusChip(),
        const SizedBox(height: AppTheme.space8),
        Text(
          _plate.isEmpty ? 'No vehicle registered' : 'Plate: $_plate',
          style: AppTheme.light.textTheme.bodyLarge,
        ),
        CustomButton(
          buttonText: _plate.isEmpty
              ? 'Connect OBU & register plate'
              : 'Re-connect OBU / change plate',
          onPressed: _openObu,
          textStyle: AppTheme.light.textTheme.labelLarge!,
          buttonColor: AppTheme.primary,
        ),
        if (_plate.isNotEmpty)
          (_plateStatus == 'stolen'
              ? CustomButton(
                  buttonText: 'Mark as recovered',
                  onPressed: _markRecovered,
                  textStyle: AppTheme.light.textTheme.labelLarge!,
                  buttonColor: AppTheme.clear,
                )
              : CustomButton(
                  buttonText: 'Report stolen',
                  onPressed: _reportStolen,
                  textStyle: AppTheme.light.textTheme.labelLarge!,
                  buttonColor: AppTheme.congested,
                )),
      ],
    );
  }

  Widget _viewAccount() {
    final name = _nameC.text.trim();
    final phone = _phoneC.text.trim();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _infoRow('Name', name.isEmpty ? '—' : name),
        _infoRow('Phone', phone.isEmpty ? '—' : phone),
        _infoRow('Email', _user?.email ?? '—'),
        CustomButton(
          buttonText: 'Edit profile',
          onPressed: () => setState(() => _editing = true),
          textStyle: AppTheme.light.textTheme.labelLarge!,
          buttonColor: AppTheme.secondary,
        ),
      ],
    );
  }

  Widget _editAccount() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextFormField(
          controller: _nameC,
          decoration: const InputDecoration(hintText: 'Name'),
        ),
        const SizedBox(height: AppTheme.space12),
        TextFormField(
          controller: _phoneC,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(hintText: 'Phone number'),
        ),
        const SizedBox(height: AppTheme.space12),
        TextFormField(
          controller: _emailC,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(hintText: 'Email'),
        ),
        CustomButton(
          buttonText: _saving ? 'Saving...' : 'Save',
          onPressed: _saving ? () {} : _saveProfile,
          textStyle: AppTheme.light.textTheme.labelLarge!,
          buttonColor: AppTheme.primary,
        ),
        TextButton(
          onPressed: _saving ? null : _cancelEdit,
          child: const Text('Cancel'),
        ),
      ],
    );
  }

  Widget _infoRow(String label, String value) {
    final text = AppTheme.light.textTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppTheme.space8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: text.bodySmall?.copyWith(color: AppTheme.textSecondary),
            ),
          ),
          Expanded(child: Text(value, style: text.bodyLarge)),
        ],
      ),
    );
  }

  Widget _header() {
    final text = AppTheme.light.textTheme;
    final name = _nameC.text.trim();
    return Row(
      children: [
        CircleAvatar(
          radius: 32,
          backgroundColor: AppTheme.secondary,
          child: const Icon(Icons.person, color: Colors.white, size: 36),
        ),
        const SizedBox(width: AppTheme.space16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name.isEmpty ? 'Driver' : name, style: text.titleLarge),
              Text(_user?.email ?? '', style: text.bodySmall),
              if (_role.isNotEmpty && _role != 'none')
                Text('Role: $_role', style: text.bodySmall),
            ],
          ),
        ),
      ],
    );
  }

  Widget _sectionTitle(String t) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.space8),
      child: Text(t, style: AppTheme.light.textTheme.titleMedium),
    );
  }

  Widget _plateStatusChip() {
    if (_plateStatus == 'none' || _plate.isEmpty) {
      return const SizedBox.shrink();
    }
    final stolen = _plateStatus == 'stolen';
    final color = stolen ? AppTheme.congested : AppTheme.clear;
    final label = stolen ? 'Reported stolen' : 'Registered';
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.space12,
          vertical: AppTheme.space4,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
        ),
        child: Text(
          label,
          style: TextStyle(color: color, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}
