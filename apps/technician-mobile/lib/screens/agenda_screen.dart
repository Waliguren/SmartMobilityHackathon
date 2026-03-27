import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import '../models/task.dart';
import 'task_detail_screen.dart';

class AgendaScreen extends StatelessWidget {
  const AgendaScreen({super.key});

  static const List<Task> _tasks = [
    Task(
      id: '1',
      titulo: 'Tarea 1',
      prioridad: TaskPriority.correctivo,
      tiempoEstimado: '2 horas',
      destino: 'Carrer de la Lleialtat, 10, 08002 Barcelona',
      destinoCoords: LatLng(41.3825, 2.1734),
    ),
    Task(
      id: '2',
      titulo: 'Tarea 2',
      prioridad: TaskPriority.preventifo,
      tiempoEstimado: '1 hora',
      destino: 'Plaça de la Mercè, 08002 Barcelona',
      destinoCoords: LatLng(41.3798, 2.1740),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Agenda")),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _tasks.length,
        itemBuilder: (context, index) {
          final task = _tasks[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              title: Text(
                task.titulo,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Chip(
                    label: Text(
                      task.prioridad == TaskPriority.correctivo
                          ? 'Correctivo'
                          : 'Preventivo',
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                    backgroundColor: task.prioridad == TaskPriority.correctivo
                        ? Colors.blue
                        : Colors.green,
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  const SizedBox(height: 4),
                  Text('Tiempo: ${task.tiempoEstimado}'),
                  Text('Destino: ${task.destino}'),
                ],
              ),
              isThreeLine: true,
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => TaskDetailScreen(task: task),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
