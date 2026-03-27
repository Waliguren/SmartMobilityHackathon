import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/task.dart';
import '../main.dart';
import 'task_detail_screen.dart';

class AgendaScreen extends StatelessWidget {
  final String? technicianId;
  final bool showAll;

  const AgendaScreen({super.key, this.technicianId, this.showAll = false});

  @override
  Widget build(BuildContext context) {
    final techId = technicianId ?? loggedTechnician?.id;

    return Scaffold(
      appBar: AppBar(title: const Text("Agenda")),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance.collection('visits').snapshots(),
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return const Center(child: Text('Error cargando tareas'));
          }
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          final allTasks = snapshot.data!.docs
              .map(
                (doc) => Task.fromFirestore(
                  doc.data() as Map<String, dynamic>,
                  doc.id,
                ),
              )
              .toList();

          List<Task> tasks;

          if (techId != null && techId.isNotEmpty) {
            if (showAll) {
              tasks = allTasks
                  .where(
                    (t) =>
                        t.technicianId.toLowerCase().trim() ==
                        techId.toLowerCase().trim(),
                  )
                  .toList();
            } else {
              tasks = allTasks
                  .where(
                    (t) =>
                        t.technicianId.toLowerCase().trim() ==
                            techId.toLowerCase().trim() &&
                        (t.status.toLowerCase().trim() == 'pendent' ||
                            t.status.toLowerCase().trim() == 'en_curs'),
                  )
                  .toList();
            }
          } else if (showAll) {
            tasks = allTasks;
          } else {
            tasks = allTasks
                .where(
                  (t) =>
                      t.status.toLowerCase().trim() == 'pendent' ||
                      t.status.toLowerCase().trim() == 'en_curs',
                )
                .toList();
          }

          if (tasks.isEmpty) {
            return const Center(child: Text('No hay tareas'));
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: tasks.length,
            itemBuilder: (context, index) {
              final task = tasks[index];
              final isPendiente = task.status == 'pendent';
              final isEnCurso = task.status == 'en_curs';
              final isCompletada = task.status == 'completada';
              Color statusColor;
              String statusText;
              if (isPendiente) {
                statusColor = Colors.red;
                statusText = 'Pendiente';
              } else if (isEnCurso) {
                statusColor = Colors.amber;
                statusText = 'En curso';
              } else {
                statusColor = Colors.green;
                statusText = 'Completada';
              }

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
                      Row(
                        children: [
                          Chip(
                            label: Text(
                              task.prioridad == TaskPriority.correctivo
                                  ? 'Correctivo'
                                  : 'Preventivo',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                              ),
                            ),
                            backgroundColor:
                                task.prioridad == TaskPriority.correctivo
                                ? Colors.blue
                                : Colors.green,
                            padding: EdgeInsets.zero,
                            materialTapTargetSize:
                                MaterialTapTargetSize.shrinkWrap,
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: statusColor,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              statusText,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
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
          );
        },
      ),
    );
  }
}
