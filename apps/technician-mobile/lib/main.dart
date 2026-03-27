import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'screens/home_screen.dart';
import 'screens/map_screen.dart';
import 'screens/agenda_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/others_screen.dart';
import 'models/technician.dart';

Technician? loggedTechnician;

String _hashPassword(String password) {
  final bytes = utf8.encode(password);
  final digest = sha256.convert(bytes);
  return digest.toString();
}

bool _verifyPassword(String inputPassword, String hashedPassword) {
  return _hashPassword(inputPassword) == hashedPassword;
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmAIrt App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const LoginScreen(),
      onGenerateRoute: (settings) {
        switch (settings.name) {
          case '/home':
            return MaterialPageRoute(builder: (_) => const HomeScreen());
          case '/map':
            return MaterialPageRoute(builder: (_) => const MapScreen());
          case '/agenda':
            return MaterialPageRoute(
              builder: (_) => AgendaScreen(technicianId: loggedTechnician?.id),
            );
          case '/profile':
            return MaterialPageRoute(
              builder: (_) => ProfileScreen(technician: loggedTechnician),
            );
          case '/others':
            return MaterialPageRoute(builder: (_) => const OthersScreen());
          default:
            return MaterialPageRoute(builder: (_) => const HomeScreen());
        }
      },
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _userController = TextEditingController(
    text: "Marc Rovira",
  );
  final TextEditingController _passController = TextEditingController(
    text: "1234",
  );
  final String _hashedPass = _hashPassword("1234");

  Future<void> _login() async {
    final username = _userController.text.trim();
    final password = _passController.text;

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Rellena todos los campos")));
      return;
    }

    if (!_verifyPassword(password, _hashedPass)) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Contraseña incorrecta")));
      return;
    }

    final snapshot = await FirebaseFirestore.instance
        .collection('technicians')
        .where('name', isEqualTo: username)
        .get();

    if (snapshot.docs.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Usuario no encontrado")));
      return;
    }

    final doc = snapshot.docs.first;
    final technician = Technician.fromFirestore(doc.data(), doc.id);

    loggedTechnician = technician;

    if (!mounted) return;
    Navigator.pushReplacementNamed(context, '/home');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          Image.asset('assets/fondo.png', fit: BoxFit.cover),
          Center(
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.8),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text("Login", style: TextStyle(fontSize: 24)),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _userController,
                    decoration: const InputDecoration(labelText: "Usuario"),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _passController,
                    decoration: const InputDecoration(labelText: "Contraseña"),
                    obscureText: true,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _login,
                    child: const Text("Iniciar sesión"),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
