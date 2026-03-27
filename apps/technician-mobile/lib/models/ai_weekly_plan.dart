class AiWeeklyPlan {
  final String engine;
  final String summary;
  final bool usedFallback;
  final List<String> preferencesAssumed;
  final List<AiScheduledTask> scheduledTasks;

  const AiWeeklyPlan({
    required this.engine,
    required this.summary,
    required this.usedFallback,
    required this.preferencesAssumed,
    required this.scheduledTasks,
  });

  factory AiWeeklyPlan.fromJson(Map<String, dynamic> json) {
    final rawPreferences =
        (json['preferences_assumed'] as List<dynamic>? ?? const <dynamic>[])
            .map((item) => item.toString())
            .toList();

    final rawTasks =
        json['scheduled_tasks'] as List<dynamic>? ?? const <dynamic>[];

    return AiWeeklyPlan(
      engine: (json['engine'] ?? '').toString(),
      summary: (json['summary'] ?? '').toString(),
      usedFallback: json['used_fallback'] == true,
      preferencesAssumed: rawPreferences,
      scheduledTasks: rawTasks
          .whereType<Map>()
          .map((item) => Map<String, dynamic>.from(item))
          .map(AiScheduledTask.fromJson)
          .toList()
        ..sort(AiScheduledTask.compareByWeekdayAndTime),
    );
  }
}

class AiScheduledTask {
  final String visitId;
  final String title;
  final String client;
  final String address;
  final String contractType;
  final String weekday;
  final String startTime;
  final String endTime;
  final double priorityScore;
  final String reason;
  final bool isBlocked;

  const AiScheduledTask({
    required this.visitId,
    required this.title,
    required this.client,
    required this.address,
    required this.contractType,
    required this.weekday,
    required this.startTime,
    required this.endTime,
    required this.priorityScore,
    required this.reason,
    this.isBlocked = false,
  });

  factory AiScheduledTask.fromJson(Map<String, dynamic> json) {
    return AiScheduledTask(
      visitId: (json['visit_id'] ?? '').toString(),
      title: (json['title'] ?? '').toString(),
      client: (json['client'] ?? '').toString(),
      address: (json['address'] ?? '').toString(),
      contractType: (json['contract_type'] ?? '').toString(),
      weekday: (json['weekday'] ?? '').toString().toLowerCase(),
      startTime: (json['start_time'] ?? '').toString(),
      endTime: (json['end_time'] ?? '').toString(),
      priorityScore: _parseDouble(json['priority_score']),
      reason: (json['reason'] ?? '').toString(),
      isBlocked: json['is_blocked'] == true,
    );
  }

  static int compareByWeekdayAndTime(
    AiScheduledTask left,
    AiScheduledTask right,
  ) {
    const dayOrder = {
      'monday': 0,
      'tuesday': 1,
      'wednesday': 2,
      'thursday': 3,
      'friday': 4,
    };

    final leftDay = dayOrder[left.weekday] ?? 99;
    final rightDay = dayOrder[right.weekday] ?? 99;
    if (leftDay != rightDay) {
      return leftDay.compareTo(rightDay);
    }

    final timeCompare = left.startTime.compareTo(right.startTime);
    if (timeCompare != 0) {
      return timeCompare;
    }

    return left.visitId.compareTo(right.visitId);
  }

  static double _parseDouble(dynamic value) {
    if (value is num) {
      return value.toDouble();
    }
    return double.tryParse(value?.toString() ?? '') ?? 0;
  }
}
