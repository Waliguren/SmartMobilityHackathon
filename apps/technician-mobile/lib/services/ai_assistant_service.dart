import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:http/http.dart' as http;

import '../models/ai_weekly_plan.dart';
import '../models/technician.dart';

class AiAssistantService {
  static const String _defaultApiBaseUrl = String.fromEnvironment(
    'FLUTTER_API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  final FirebaseFirestore _firestore;
  final http.Client _client;
  final String _apiBaseUrl;

  AiAssistantService({
    FirebaseFirestore? firestore,
    http.Client? client,
    String? apiBaseUrl,
  }) : _firestore = firestore ?? FirebaseFirestore.instance,
       _client = client ?? http.Client(),
       _apiBaseUrl = (apiBaseUrl ?? _defaultApiBaseUrl).replaceAll(
         RegExp(r'/$'),
         '',
       );

  Future<AiWeeklyPlan> generateWeeklyPlan({
    required Technician technician,
  }) async {
    final visitsSnapshot = await _firestore
        .collection('visits')
        .where('technician_id', isEqualTo: technician.id)
        .where('status', whereIn: ['pendent', 'en_curs'])
        .get();

    if (visitsSnapshot.docs.isEmpty) {
      throw StateError('No hay tareas pendientes para planificar.');
    }

    final incidencesSnapshot = await _firestore.collection('incidences').get();
    final contractsSnapshot = await _firestore.collection('contracts').get();

    final incidencesById = {
      for (final doc in incidencesSnapshot.docs) doc.id: doc.data(),
    };
    final contractsByChargerId = {
      for (final doc in contractsSnapshot.docs)
        (doc.data()['charger_id'] ?? '').toString(): doc.data(),
    };

    final tasksPayload = visitsSnapshot.docs.map((doc) {
      final visit = doc.data();
      final incidenceId = (visit['incidence_id'] ?? '').toString();
      final incidence = incidencesById[incidenceId] ?? const <String, dynamic>{};
      final chargerId = (incidence['charger_id'] ?? '').toString();
      final contract =
          contractsByChargerId[chargerId] ?? const <String, dynamic>{};

      final visitType = (visit['visit_type'] ?? 'manteniment').toString();
      final priority = (incidence['priority'] ?? 'mitja').toString();
      final client = (contract['client_id'] ?? 'Cliente sin contrato').toString();
      final contractType = (contract['type'] ?? 'Estándar').toString();

      return <String, dynamic>{
        'visit_id': doc.id,
        'title': '${_formatVisitType(visitType)} - $client',
        'address': (visit['address'] ?? '').toString(),
        'status': (visit['status'] ?? '').toString(),
        'visit_type': visitType,
        'priority': priority,
        'client': client,
        'contract_type': contractType,
        'estimated_minutes': _estimateMinutes(visitType, priority, contractType),
        'description': (incidence['description'] ?? '').toString(),
        'created_at': _timestampToIsoString(incidence['created_at']),
        'planned_date': _timestampToIsoString(visit['planned_date']),
      };
    }).toList();

    final uri = Uri.parse('$_apiBaseUrl/api/v1/planning/ai-weekly-plan');
    final response = await _client.post(
      uri,
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'week_start_date': _mondayOfCurrentWeek().toIso8601String().split('T')[0],
        'technician_id': technician.id,
        'technician_name': technician.name,
        'technician_zone': technician.zone,
        'tasks': tasksPayload,
      }),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw StateError(
        'No se pudo generar el planning IA (${response.statusCode}).',
      );
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('La respuesta del backend no es válida.');
    }

    return AiWeeklyPlan.fromJson(decoded);
  }

  static DateTime _mondayOfCurrentWeek() {
    final now = DateTime.now();
    return DateTime(now.year, now.month, now.day).subtract(
      Duration(days: now.weekday - DateTime.monday),
    );
  }

  static String _formatVisitType(String visitType) {
    switch (visitType.toLowerCase()) {
      case 'avaria':
      case 'corrective':
      case 'correctivo':
        return 'Avería';
      case 'manteniment':
      case 'mantenimiento':
        return 'Mantenimiento';
      default:
        return visitType;
    }
  }

  static int _estimateMinutes(
    String visitType,
    String priority,
    String contractType,
  ) {
    final normalizedVisitType = visitType.toLowerCase();
    final normalizedPriority = priority.toLowerCase();
    final normalizedContract = contractType.toLowerCase();

    if (normalizedVisitType == 'avaria' || normalizedPriority == 'alta') {
      return 120;
    }
    if (normalizedContract.contains('premium')) {
      return 90;
    }
    return 60;
  }

  static String? _timestampToIsoString(dynamic value) {
    if (value is Timestamp) {
      return value.toDate().toIso8601String();
    }
    return null;
  }
}
