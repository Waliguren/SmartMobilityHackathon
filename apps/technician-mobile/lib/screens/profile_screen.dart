import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/technician.dart';
import 'agenda_screen.dart';

class ProfileScreen extends StatefulWidget {
  final Technician? technician;

  const ProfileScreen({super.key, this.technician});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  int _pendingTasks = 0;

  @override
  void initState() {
    super.initState();
    _loadPendingTasks();
  }

  Future<void> _loadPendingTasks() async {
    if (widget.technician == null) return;

    final snapshot = await FirebaseFirestore.instance
        .collection('visits')
        .where('technician_id', isEqualTo: widget.technician!.id)
        .where('status', whereIn: ['pendent', 'en_curs'])
        .get();

    if (mounted) {
      setState(() {
        _pendingTasks = snapshot.docs.length;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.technician == null) {
      return Scaffold(
        appBar: AppBar(title: const Text("Perfil")),
        body: const Center(child: Text("No hay usuario logeado")),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text("Perfil")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            CircleAvatar(
              radius: 60,
              backgroundImage: const AssetImage('assets/fondo.png'),
              child: Text(
                widget.technician!.name.isNotEmpty
                    ? widget.technician!.name[0].toUpperCase()
                    : '?',
                style: const TextStyle(fontSize: 40, color: Colors.white),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              widget.technician!.name,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              "Zona: ${widget.technician!.zone}",
              style: const TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.check_circle_outline),
                title: const Text("Especialista"),
                trailing: Text(widget.technician!.expert ? "Sí" : "No"),
              ),
            ),
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.bar_chart),
                title: const Text("Nivel de experiencia"),
                trailing: Text(widget.technician!.expertise.toString()),
              ),
            ),
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.badge),
                title: const Text("ID de técnico"),
                trailing: Text(widget.technician!.id),
              ),
            ),
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.task),
                title: const Text("Tareas"),
                trailing: Text(
                  _pendingTasks.toString(),
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => AgendaScreen(
                        technicianId: widget.technician!.id,
                        showAll: true,
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
