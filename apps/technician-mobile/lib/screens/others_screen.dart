import 'package:flutter/material.dart';

class OthersScreen extends StatelessWidget {
  const OthersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Otros")),
      body: const Center(
        child: Text("Aquí irá la sección de otros"),
      ),
    );
  }
}