import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  LatLng? _currentLocation;
  LatLng? _destination;
  List<LatLng> _routePoints = [];

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
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
      ),
    );

    if (!mounted) return;

    setState(() {
      _currentLocation = LatLng(position.latitude, position.longitude);
    });
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
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error obteniendo la ruta')),
      );
    }
  }

  void _setDestination(LatLng point) {
    setState(() {
      _destination = point;
    });

    if (_currentLocation != null) {
      _getRoute(_currentLocation!, point);
    }
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
          builder: (ctx) => const Icon(Icons.location_pin, color: Colors.blue, size: 40),
        ),
      );
    }

    if (_destination != null) {
      markers.add(
        Marker(
          width: 80,
          height: 80,
          point: _destination!,
          builder: (ctx) => const Icon(Icons.location_pin, color: Colors.red, size: 40),
        ),
      );
    }

    return Scaffold(
      body: FlutterMap(
        options: MapOptions(
          center: center,
          zoom: 14.0,
          onTap: (tapPos, point) {
            _setDestination(point); // Toca para poner destino
          },
        ),
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
}