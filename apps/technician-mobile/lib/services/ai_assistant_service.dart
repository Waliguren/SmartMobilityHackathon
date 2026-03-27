import 'package:cloud_firestore/cloud_firestore.dart';

import '../models/ai_weekly_plan.dart';
import '../models/technician.dart';

class AiAssistantService {
  final FirebaseFirestore _firestore;

  AiAssistantService({
    FirebaseFirestore? firestore,
  }) : _firestore = firestore ?? FirebaseFirestore.instance;

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

    final tasks = visitsSnapshot.docs.map((doc) {
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
      final createdAt = _timestampToDateTime(incidence['created_at']);
      final plannedDate = _timestampToDateTime(visit['planned_date']);
      final estimatedMinutes = _estimateMinutes(visitType, priority, contractType);
      final priorityScore = _priorityScore(
        visitType: visitType,
        priority: priority,
        contractType: contractType,
        status: (visit['status'] ?? '').toString(),
        createdAt: createdAt,
      );

      return _PlanningTask(
        visitId: doc.id,
        title: '${_formatVisitType(visitType)} - $client',
        address: (visit['address'] ?? '').toString(),
        client: client,
        contractType: contractType,
        visitType: visitType,
        priority: priority,
        status: (visit['status'] ?? '').toString(),
        description: (incidence['description'] ?? '').toString(),
        estimatedMinutes: estimatedMinutes,
        createdAt: createdAt,
        plannedDate: plannedDate,
        priorityScore: priorityScore,
      );
    }).toList()
      ..sort((left, right) {
        final scoreCompare = right.priorityScore.compareTo(left.priorityScore);
        if (scoreCompare != 0) {
          return scoreCompare;
        }

        final createdAtCompare = _compareNullableDateTimes(
          left.createdAt,
          right.createdAt,
        );
        if (createdAtCompare != 0) {
          return createdAtCompare;
        }

        final plannedDateCompare = _compareNullableDateTimes(
          left.plannedDate,
          right.plannedDate,
        );
        if (plannedDateCompare != 0) {
          return plannedDateCompare;
        }

        return left.visitId.compareTo(right.visitId);
      });

    final scheduledTasks = _buildDeterministicSchedule(tasks);

    final topClients = tasks
        .take(3)
        .map((task) => task.client)
        .toSet()
        .join(', ');

    return AiWeeklyPlan(
      engine: 'deterministic-local-planner',
      summary:
          'Plan semanal concentrado en dos días, priorizando averías, SLA y clientes con contratos de mayor valor${topClients.isNotEmpty ? ' como $topClients' : ''}.',
      usedFallback: false,
      preferencesAssumed: const [
        'Martes 12:30 - 14:30 reservado para una comida personal.',
        'Jueves desde las 16:00 bloqueado por partido.',
        'Horario operativo de lunes a viernes de 09:00 a 13:00 y de 15:00 a 18:00.',
      ],
      scheduledTasks: scheduledTasks,
    );
  }

  static List<AiScheduledTask> _buildDeterministicSchedule(
    List<_PlanningTask> tasks,
  ) {
    final windows = _buildWindows();
    final scheduled = <AiScheduledTask>[];
    var overflowCursor = DateTime(2026, 1, 3, 15, 0);

    for (final task in tasks) {
      final durationMinutes = task.estimatedMinutes.clamp(45, 180) as int;
      final slot = _allocateSlot(windows, durationMinutes);

      late final String weekday;
      late final DateTime start;
      late final DateTime end;

      if (slot == null) {
        weekday = 'wednesday';
        start = overflowCursor;
        end = start.add(Duration(minutes: durationMinutes));
        overflowCursor = end.add(const Duration(minutes: 15));
      } else {
        weekday = slot.weekday;
        start = slot.start;
        end = slot.end;
      }

      scheduled.add(
        AiScheduledTask(
          visitId: task.visitId,
          title: task.title,
          client: task.client,
          address: task.address,
          contractType: task.contractType,
          weekday: weekday,
          startTime: _formatTime(start),
          endTime: _formatTime(end),
          priorityScore: task.priorityScore,
          reason:
              'Asignada por prioridad ${task.priority.toLowerCase()}, contrato ${task.contractType} y tipo ${_formatVisitType(task.visitType).toLowerCase()}.',
        ),
      );
    }

    scheduled.add(
      const AiScheduledTask(
        visitId: 'calendar-block-tuesday-lunch',
        title: 'Incompatibilidad del técnico',
        client: 'Calendario personal',
        address: 'Comida reservada',
        contractType: 'Bloqueo',
        weekday: 'tuesday',
        startTime: '12:30',
        endTime: '14:30',
        priorityScore: 0,
        reason: 'Franja no disponible y debe respetarse en la planificación.',
        isBlocked: true,
      ),
    );

    scheduled.sort(AiScheduledTask.compareByWeekdayAndTime);
    return scheduled;
  }

  static List<_MutablePlanningWindow> _buildWindows() {
    const baseDate = 2026;
    return const [
      _PlanningWindow('monday', 1, 9, 0, 13, 0),
      _PlanningWindow('monday', 1, 15, 0, 18, 0),
      _PlanningWindow('wednesday', 3, 9, 0, 13, 0),
      _PlanningWindow('wednesday', 3, 15, 0, 18, 0),
    ].map((window) {
      return window.toMutable(baseDate);
    }).toList();
  }

  static _AllocatedSlot? _allocateSlot(
    List<_MutablePlanningWindow> windows,
    int durationMinutes,
  ) {
    final duration = Duration(minutes: durationMinutes);

    for (final window in windows) {
      if (window.end.difference(window.start) < duration) {
        continue;
      }

      final start = window.start;
      final end = start.add(duration);
      window.start = end.add(const Duration(minutes: 15));
      return _AllocatedSlot(weekday: window.weekday, start: start, end: end);
    }

    return null;
  }

  static int _compareNullableDateTimes(DateTime? left, DateTime? right) {
    if (left == null && right == null) {
      return 0;
    }
    if (left == null) {
      return 1;
    }
    if (right == null) {
      return -1;
    }
    return left.compareTo(right);
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

  static double _priorityScore({
    required String visitType,
    required String priority,
    required String contractType,
    required String status,
    required DateTime? createdAt,
  }) {
    final contractScore = _contractScore(contractType);
    final severityScore = _severityScore(priority);
    final visitTypeScore = _visitTypeScore(visitType);
    final statusScore = _statusScore(status);
    final ageScore = _ageScore(createdAt);

    final weightedScore =
        (contractScore * 0.40) +
        (severityScore * 0.25) +
        (visitTypeScore * 0.15) +
        (statusScore * 0.10) +
        (ageScore * 0.10);

    return double.parse(weightedScore.toStringAsFixed(1));
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

  static double _contractScore(String contractType) {
    final normalizedContract = contractType.toLowerCase();
    if (normalizedContract.contains('premium')) {
      return 100;
    }
    if (normalizedContract.contains('or') ||
        normalizedContract.contains('oro') ||
        normalizedContract.contains('gold')) {
      return 88;
    }
    if (normalizedContract.contains('bàsic') ||
        normalizedContract.contains('basic')) {
      return 55;
    }
    return 70;
  }

  static double _severityScore(String priority) {
    final normalizedPriority = priority.toLowerCase();
    if (normalizedPriority == 'alta') {
      return 100;
    }
    if (normalizedPriority == 'mitja' || normalizedPriority == 'media') {
      return 72;
    }
    return 45;
  }

  static double _visitTypeScore(String visitType) {
    final normalizedVisitType = visitType.toLowerCase();
    if (normalizedVisitType == 'avaria' ||
        normalizedVisitType == 'correctivo' ||
        normalizedVisitType == 'corrective') {
      return 100;
    }
    return 60;
  }

  static double _statusScore(String status) {
    final normalizedStatus = status.toLowerCase();
    if (normalizedStatus == 'en_curs') {
      return 90;
    }
    if (normalizedStatus == 'pendent') {
      return 75;
    }
    return 40;
  }

  static double _ageScore(DateTime? createdAt) {
    if (createdAt == null) {
      return 55;
    }

    final elapsedHours = DateTime.now().difference(createdAt).inHours;
    final normalizedHours = elapsedHours < 0 ? 0 : elapsedHours;
    final score = 55 + (normalizedHours / 6);
    return score > 100 ? 100 : score;
  }

  static DateTime? _timestampToDateTime(dynamic value) {
    if (value is Timestamp) {
      return value.toDate();
    }
    return null;
  }

  static String _formatTime(DateTime dateTime) {
    final hours = dateTime.hour.toString().padLeft(2, '0');
    final minutes = dateTime.minute.toString().padLeft(2, '0');
    return '$hours:$minutes';
  }
}

class _PlanningTask {
  final String visitId;
  final String title;
  final String address;
  final String client;
  final String contractType;
  final String visitType;
  final String priority;
  final String status;
  final String description;
  final int estimatedMinutes;
  final DateTime? createdAt;
  final DateTime? plannedDate;
  final double priorityScore;

  const _PlanningTask({
    required this.visitId,
    required this.title,
    required this.address,
    required this.client,
    required this.contractType,
    required this.visitType,
    required this.priority,
    required this.status,
    required this.description,
    required this.estimatedMinutes,
    required this.createdAt,
    required this.plannedDate,
    required this.priorityScore,
  });
}

class _PlanningWindow {
  final String weekday;
  final int day;
  final int startHour;
  final int startMinute;
  final int endHour;
  final int endMinute;

  const _PlanningWindow(
    this.weekday,
    this.day,
    this.startHour,
    this.startMinute,
    this.endHour,
    this.endMinute,
  );

  _MutablePlanningWindow toMutable(int year) {
    return _MutablePlanningWindow(
      weekday: weekday,
      start: DateTime(year, 1, day, startHour, startMinute),
      end: DateTime(year, 1, day, endHour, endMinute),
    );
  }
}

class _MutablePlanningWindow {
  final String weekday;
  DateTime start;
  final DateTime end;

  _MutablePlanningWindow({
    required this.weekday,
    required this.start,
    required this.end,
  });
}

class _AllocatedSlot {
  final String weekday;
  final DateTime start;
  final DateTime end;

  const _AllocatedSlot({
    required this.weekday,
    required this.start,
    required this.end,
  });
}
