import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert';
import '../models/task.dart';
import '../main.dart';

class TaskDetailScreen extends StatefulWidget {
  final Task task;

  const TaskDetailScreen({super.key, required this.task});

  @override
  State<TaskDetailScreen> createState() => _TaskDetailScreenState();
}

class _TaskDetailScreenState extends State<TaskDetailScreen> {
  LatLng? _currentLocation;
  List<LatLng> _routePoints = [];
  bool _isMapExpanded = false;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    Position position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
    );

    if (!mounted) return;

    setState(() {
      _currentLocation = LatLng(position.latitude, position.longitude);
    });

    _getRoute(_currentLocation!, widget.task.destinoCoords);
  }

  Future<void> _getRoute(LatLng start, LatLng end) async {
    final url =
        'http://router.project-osrm.org/route/v1/driving/${start.longitude},${start.latitude};${end.longitude},${end.latitude}?overview=full&geometries=geojson';

    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final coords = data['routes'][0]['geometry']['coordinates'] as List;

      final points = coords
          .map((c) => LatLng(c[1] as double, c[0] as double))
          .toList();

      setState(() {
        _routePoints = points;
      });
    }
  }

  Future<void> _openGoogleMaps() async {
    final dest = widget.task.destinoCoords;

    final urlString =
        'https://www.google.com/maps/search/?api=1&query=${dest.latitude},${dest.longitude}';

    final uri = Uri.parse(urlString);

    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (e) {
      try {
        final fallbackUri = Uri.parse(
          'https://maps.google.com/?q=${dest.latitude},${dest.longitude}',
        );
        await launchUrl(fallbackUri, mode: LaunchMode.externalApplication);
      } catch (e2) {
        if (!mounted) return;
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error al abrir mapas: $e2')));
      }
    }
  }

  void _toggleMapExpanded() {
    setState(() {
      _isMapExpanded = !_isMapExpanded;
    });
  }

  Future<void> _startTask() async {
    try {
      final now = DateTime.now();
      final startTimeSeconds = now.millisecondsSinceEpoch ~/ 1000;

      await FirebaseFirestore.instance
          .collection('visits')
          .doc(widget.task.id)
          .update({'status': 'en_curs', 'start_time': startTimeSeconds});

      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Tarea iniciada')));
      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error al iniciar tarea: $e')));
    }
  }

  void _openReportForm() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => ReportFormSheet(task: widget.task),
    );
  }

  @override
  Widget build(BuildContext context) {
    final center = _currentLocation ?? LatLng(41.1189, 1.2445);

    final markers = <Marker>[];
    if (_currentLocation != null) {
      markers.add(
        Marker(
          width: 80,
          height: 80,
          point: _currentLocation!,
          builder: (ctx) =>
              const Icon(Icons.location_pin, color: Colors.blue, size: 40),
        ),
      );
    }

    markers.add(
      Marker(
        width: 80,
        height: 80,
        point: widget.task.destinoCoords,
        builder: (ctx) =>
            const Icon(Icons.location_pin, color: Colors.red, size: 40),
      ),
    );

    if (_isMapExpanded) {
      return Scaffold(
        appBar: AppBar(
          title: Text(widget.task.titulo),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: FlutterMap(
          options: MapOptions(center: center, zoom: 14.0),
          children: [
            TileLayer(
              urlTemplate: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
              subdomains: const ['a', 'b', 'c'],
              userAgentPackageName: 'com.example.smairt',
            ),
            MarkerLayer(markers: markers),
            if (_routePoints.isNotEmpty)
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: _routePoints,
                    color: Colors.blue,
                    strokeWidth: 4,
                  ),
                ],
              ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text(widget.task.titulo)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.task.titulo,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Chip(
              label: Text(
                widget.task.prioridad == TaskPriority.correctivo
                    ? 'Correctivo'
                    : 'Preventivo',
                style: const TextStyle(color: Colors.white),
              ),
              backgroundColor: widget.task.prioridad == TaskPriority.correctivo
                  ? Colors.blue
                  : Colors.green,
            ),
            const SizedBox(height: 8),
            Text('Tiempo estimado: ${widget.task.tiempoEstimado}'),
            const SizedBox(height: 4),
            Text('Destino: ${widget.task.destino}'),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _openGoogleMaps,
              icon: const Icon(Icons.navigation),
              label: const Text('Navegar con GPS'),
            ),
            if (widget.task.status == 'pendent' &&
                widget.task.technicianId.isNotEmpty) ...[
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: _startTask,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Comenzar tarea'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              ),
            ],
            if (widget.task.status == 'en_curs') ...[
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: _openReportForm,
                icon: const Icon(Icons.description),
                label: const Text('Informe'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.grey),
              ),
            ],
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: SizedBox(
                height: 200,
                child: FlutterMap(
                  options: MapOptions(center: center, zoom: 13.0),
                  children: [
                    TileLayer(
                      urlTemplate:
                          "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                      subdomains: const ['a', 'b', 'c'],
                      userAgentPackageName: 'com.example.smairt',
                    ),
                    MarkerLayer(markers: markers),
                    if (_routePoints.isNotEmpty)
                      PolylineLayer(
                        polylines: [
                          Polyline(
                            points: _routePoints,
                            color: Colors.blue,
                            strokeWidth: 4,
                          ),
                        ],
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: IconButton(
                onPressed: _toggleMapExpanded,
                icon: const Icon(Icons.add_circle, size: 32),
                tooltip: 'Ampliar mapa',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ReportFormSheet extends StatefulWidget {
  final Task task;

  const ReportFormSheet({super.key, required this.task});

  @override
  State<ReportFormSheet> createState() => _ReportFormSheetState();
}

class _ReportFormSheetState extends State<ReportFormSheet> {
  final _formKey = GlobalKey<FormState>();
  final _observationsController = TextEditingController();
  String _reportType = 'Reparacio';
  bool _isLoading = false;

  final List<String> _reportTypes = [
    'Reparacio',
    'Urgencia',
    'Preventiu',
    'Inspeccio',
  ];

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}:${time.second.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _observationsController.dispose();
    super.dispose();
  }

  Future<bool> _saveReport(String reportStatus) async {
    if (!_formKey.currentState!.validate()) return false;

    setState(() => _isLoading = true);

    final now = DateTime.now();
    final startTime = widget.task.displayStartTime;

    try {
      await FirebaseFirestore.instance.collection('reports').add({
        'visit_id': widget.task.id,
        'technician_id': loggedTechnician?.id ?? '',
        'report_type': _reportType,
        'status': reportStatus,
        'observations': _observationsController.text,
        'created_at': FieldValue.serverTimestamp(),
        'start_time': startTime?.millisecondsSinceEpoch != null
            ? (startTime!.millisecondsSinceEpoch ~/ 1000)
            : null,
        'end_time': now.millisecondsSinceEpoch ~/ 1000,
      });

      await FirebaseFirestore.instance
          .collection('visits')
          .doc(widget.task.id)
          .update({'end_time': now.millisecondsSinceEpoch ~/ 1000});

      return true;
    } catch (e) {
      if (!mounted) return false;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error al guardar: $e')));
      return false;
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _finalizeTask() async {
    final success = await _saveReport('firmat');
    if (!success || !mounted) return;

    try {
      await FirebaseFirestore.instance
          .collection('visits')
          .doc(widget.task.id)
          .update({'status': 'completada'});

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tarea finalizada correctamente')),
      );
      Navigator.pop(context);
      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error al actualizar tarea: $e')));
    }
  }

  Future<void> _pendingReview() async {
    final success = await _saveReport('esborrany');
    if (!success || !mounted) return;

    try {
      await FirebaseFirestore.instance
          .collection('visits')
          .doc(widget.task.id)
          .update({'technician_id': null, 'status': 'pendent'});

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tarea pendiente de revisión')),
      );
      Navigator.pop(context);
      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error al actualizar tarea: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
        left: 16,
        right: 16,
        top: 16,
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Nuevo Informe',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hora de inicio: ${_formatTime(widget.task.displayStartTime)}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Tiempo en curso: ${widget.task.formattedDuration}',
                    style: const TextStyle(fontSize: 16, color: Colors.blue),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _reportType,
              decoration: const InputDecoration(
                labelText: 'Tipo de informe',
                border: OutlineInputBorder(),
              ),
              items: _reportTypes.map((type) {
                return DropdownMenuItem(value: type, child: Text(type));
              }).toList(),
              onChanged: (value) {
                if (value != null) setState(() => _reportType = value);
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _observationsController,
              decoration: const InputDecoration(
                labelText: 'Observaciones',
                border: OutlineInputBorder(),
              ),
              maxLines: 4,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Por favor, añade observaciones';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _finalizeTask,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('Tarea finalizada'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _pendingReview,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                    ),
                    child: const Text('Pendiente de revisión'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
