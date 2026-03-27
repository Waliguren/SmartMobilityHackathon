import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'dart:convert';
import '../models/task.dart';

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
    final url = Uri.parse(
      'https://www.google.com/maps/dir/?api=1&destination=${dest.latitude},${dest.longitude}',
    );
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  void _toggleMapExpanded() {
    setState(() {
      _isMapExpanded = !_isMapExpanded;
    });
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
