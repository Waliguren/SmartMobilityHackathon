import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          Image.asset('assets/fondo.png', fit: BoxFit.cover),
          Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: const [
              SizedBox(height: 80),
              Text(
                "Bienvenido!",
                style: TextStyle(
                  fontSize: 32,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
      bottomNavigationBar: BottomAppBar(
        color: Colors.white.withOpacity(0.9),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              IconButton(
                icon: const Icon(Icons.map),
                onPressed: () => Navigator.pushNamed(context, '/map'),
              ),
              IconButton(
                icon: const Icon(Icons.event_note),
                onPressed: () => Navigator.pushNamed(context, '/agenda'),
              ),
              IconButton(
                icon: const Icon(Icons.person),
                onPressed: () => Navigator.pushNamed(context, '/profile'),
              ),
              IconButton(
                icon: const Icon(Icons.more_horiz),
                onPressed: () => Navigator.pushNamed(context, '/others'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}