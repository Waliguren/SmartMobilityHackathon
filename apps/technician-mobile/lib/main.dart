import "package:flutter/material.dart";

void main() {
  runApp(const TechnicianApp());
}

class TechnicianApp extends StatelessWidget {
  const TechnicianApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Technician Mobile",
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: Text("Scaffold inicial creado. Sin funcionalidad implementada."),
        ),
      ),
    );
  }
}