import 'package:latlong2/latlong.dart';

enum TaskPriority { correctivo, preventifo }

class Task {
  final String id;
  final String titulo;
  final TaskPriority prioridad;
  final String tiempoEstimado;
  final String destino;
  final LatLng destinoCoords;
  final String status;
  final String incidenceId;
  final String technicianId;

  const Task({
    required this.id,
    required this.titulo,
    required this.prioridad,
    required this.tiempoEstimado,
    required this.destino,
    required this.destinoCoords,
    required this.status,
    required this.incidenceId,
    required this.technicianId,
  });

  factory Task.fromFirestore(Map<String, dynamic> data, String docId) {
    final location = data['location'] as Map<String, dynamic>?;
    final lat = location?['_latitude'] ?? 0.0;
    final lng = location?['_longitude'] ?? 0.0;

    final priorityStr = (data['priority'] ?? 'mitja').toString().toLowerCase();
    TaskPriority prioridad;
    if (priorityStr == 'alta') {
      prioridad = TaskPriority.correctivo;
    } else {
      prioridad = TaskPriority.preventifo;
    }

    final visitType = (data['visit_type'] ?? 'manteniment').toString();
    final incidenceId = (data['incidence_id'] ?? '').toString();
    final technicianId = (data['technician_id'] ?? '').toString();

    return Task(
      id: docId,
      titulo: '$visitType - $incidenceId',
      prioridad: prioridad,
      tiempoEstimado: '1 hora',
      destino: (data['address'] ?? '').toString(),
      destinoCoords: LatLng(lat, lng),
      status: (data['status'] ?? '').toString(),
      incidenceId: incidenceId,
      technicianId: technicianId,
    );
  }
}
