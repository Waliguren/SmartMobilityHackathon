import 'package:latlong2/latlong.dart';

enum TaskPriority { correctivo, preventifo }

class Task {
  final String id;
  final String titulo;
  final TaskPriority prioridad;
  final String tiempoEstimado;
  final String destino;
  final LatLng destinoCoords;

  const Task({
    required this.id,
    required this.titulo,
    required this.prioridad,
    required this.tiempoEstimado,
    required this.destino,
    required this.destinoCoords,
  });
}
