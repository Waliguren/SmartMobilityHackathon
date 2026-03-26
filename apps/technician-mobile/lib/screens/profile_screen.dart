import 'package:flutter/material.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  // Datos de ejemplo
  final String profileImage = 'assets/fondo.png'; // Cambia por tu foto de perfil
  final String name = 'Juan Pérez';
  final bool especialista = true;
  final String nivelExperiencia = 'Avanzado';
  final int tareasPendientes = 5;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Perfil")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Foto de perfil
            CircleAvatar(
              radius: 60,
              backgroundImage: AssetImage(profileImage),
            ),
            const SizedBox(height: 16),

            // Nombre
            Text(
              name,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            // Especialista
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.check_circle_outline),
                title: const Text("Especialista"),
                trailing: Text(especialista ? "Sí" : "No"),
              ),
            ),

            // Nivel de experiencia
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.bar_chart),
                title: const Text("Nivel de experiencia"),
                trailing: Text(nivelExperiencia),
              ),
            ),

            // Tareas pendientes
            Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: ListTile(
                leading: const Icon(Icons.task),
                title: const Text("Tareas pendientes esta semana"),
                trailing: Text(tareasPendientes.toString()),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
