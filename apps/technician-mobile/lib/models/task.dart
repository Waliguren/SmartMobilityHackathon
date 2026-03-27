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
  final DateTime? startTime;
  final DateTime? endTime;

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
    this.startTime,
    this.endTime,
  });

  Duration get duration {
    final start =
        startTime ??
        DateTime(
          DateTime.now().year,
          DateTime.now().month,
          DateTime.now().day,
          6,
          0,
          0,
        );
    final end = endTime ?? DateTime.now();
    return end.difference(start);
  }

  String get formattedDuration {
    final dur = duration;
    final hours = dur.inHours;
    final minutes = dur.inMinutes.remainder(60);
    final seconds = dur.inSeconds.remainder(60);
    return '${hours}h ${minutes}m ${seconds}s';
  }

  DateTime get displayStartTime {
    return startTime ??
        DateTime(
          DateTime.now().year,
          DateTime.now().month,
          DateTime.now().day,
          6,
          0,
          0,
        );
  }

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

    DateTime? startTime;
    DateTime? endTime;
    if (data['start_time'] != null) {
      if (data['start_time'] is int) {
        startTime = DateTime.fromMillisecondsSinceEpoch(
          data['start_time'] * 1000,
        );
      }
    }
    if (data['end_time'] != null) {
      if (data['end_time'] is int) {
        endTime = DateTime.fromMillisecondsSinceEpoch(data['end_time'] * 1000);
      }
    }

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
      startTime: startTime,
      endTime: endTime,
    );
  }
}
