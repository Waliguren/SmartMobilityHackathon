import 'package:flutter/material.dart';

import '../main.dart';
import '../models/ai_weekly_plan.dart';
import '../services/ai_assistant_service.dart';

class AiAssistantScreen extends StatefulWidget {
  const AiAssistantScreen({super.key});

  @override
  State<AiAssistantScreen> createState() => _AiAssistantScreenState();
}

class _AiAssistantScreenState extends State<AiAssistantScreen> {
  final AiAssistantService _assistantService = AiAssistantService();

  bool _isGenerating = false;
  String? _errorMessage;
  AiWeeklyPlan? _plan;

  Future<void> _generatePlan() async {
    final technician = loggedTechnician;
    if (technician == null) {
      setState(() {
        _errorMessage = 'No hay técnico logeado.';
      });
      return;
    }

    setState(() {
      _isGenerating = true;
      _errorMessage = null;
    });

    try {
      final plan = await _assistantService.generateWeeklyPlan(
        technician: technician,
      );

      if (!mounted) return;
      setState(() {
        _plan = plan;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _errorMessage = _humanizeError(error);
      });
    } finally {
      if (!mounted) return;
      setState(() {
        _isGenerating = false;
      });
    }
  }

  String _humanizeError(Object error) {
    final message = error.toString();
    if (message.contains('No hay tareas pendientes')) {
      return 'No hay tareas pendientes para esta semana.';
    }
    return 'No se pudo generar el planning semanal.';
  }

  Map<String, List<AiScheduledTask>> _groupTasksByDay(List<AiScheduledTask> tasks) {
    final grouped = {
      'monday': <AiScheduledTask>[],
      'tuesday': <AiScheduledTask>[],
      'wednesday': <AiScheduledTask>[],
      'thursday': <AiScheduledTask>[],
      'friday': <AiScheduledTask>[],
    };

    for (final task in tasks) {
      grouped.putIfAbsent(task.weekday, () => <AiScheduledTask>[]).add(task);
    }

    return grouped;
  }

  @override
  Widget build(BuildContext context) {
    final technician = loggedTechnician;

    return Scaffold(
      appBar: AppBar(title: const Text('AI-Assistant')),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF5F8FF), Color(0xFFE8F0FE)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _SectionCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Planificador Semanal IA',
                    style: Theme.of(
                      context,
                    ).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Genera una agenda de lunes a viernes priorizando tareas críticas, SLA y clientes con contratos más valiosos.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _InfoChip(
                        icon: Icons.person_pin_circle_outlined,
                        label: technician?.name ?? 'Sin técnico',
                      ),
                      const _InfoChip(
                        icon: Icons.priority_high,
                        label: 'SLA > criticidad > preventivo',
                      ),
                      const _InfoChip(
                        icon: Icons.rule,
                        label: 'Planificación determinista',
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isGenerating ? null : _generatePlan,
                      icon: _isGenerating
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.auto_awesome),
                      label: const Text('Planificador Semanal IA'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            const _SectionCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Preferencias del técnico',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 10),
                  _PreferenceRow(
                    icon: Icons.lunch_dining,
                    text: 'Martes 12:30 - 14:30: comida personal bloqueada',
                  ),
                  SizedBox(height: 8),
                  _PreferenceRow(
                    icon: Icons.sports_soccer,
                    text: 'Jueves desde las 16:00: partido y tarde cerrada',
                  ),
                ],
              ),
            ),
            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              _SectionCard(
                backgroundColor: const Color(0xFFFFF1F0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.error_outline, color: Colors.redAccent),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.redAccent),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            if (_plan != null) ...[
              const SizedBox(height: 16),
              _SectionCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            'Plan generado',
                            style: Theme.of(context).textTheme.titleLarge
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ),
                        const Chip(
                          label: Text('Determinista'),
                          backgroundColor: Color(0xFFD8F5D0),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(_plan!.summary),
                    const SizedBox(height: 12),
                    ..._plan!.preferencesAssumed.map(
                      (preference) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Text('• $preference'),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              ..._weekdaySections(
                _groupTasksByDay(_plan?.scheduledTasks ?? const <AiScheduledTask>[]),
              ),
            ],
          ],
        ),
      ),
    );
  }

  List<Widget> _weekdaySections(Map<String, List<AiScheduledTask>> groupedPlan) {
    const weekdayLabels = {
      'monday': 'Lunes',
      'tuesday': 'Martes',
      'wednesday': 'Miércoles',
      'thursday': 'Jueves',
      'friday': 'Viernes',
    };

    final widgets = <Widget>[];

    for (final entry in weekdayLabels.entries) {
      final tasks = groupedPlan[entry.key] ?? const <AiScheduledTask>[];
      widgets.add(
        _SectionCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                entry.value,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              if (tasks.isEmpty)
                const Text(
                  'Sin tareas asignadas.',
                  style: TextStyle(color: Colors.black54),
                )
              else
                ...tasks.map(_TaskPlanTile.new),
            ],
          ),
        ),
      );
      widgets.add(const SizedBox(height: 12));
    }

    if (widgets.isNotEmpty) {
      widgets.removeLast();
    }

    return widgets;
  }
}

class _SectionCard extends StatelessWidget {
  final Widget child;
  final Color? backgroundColor;

  const _SectionCard({required this.child, this.backgroundColor});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 1,
      color: backgroundColor ?? Colors.white.withValues(alpha: 0.96),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: child,
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF2FF),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: Colors.blueGrey.shade700),
          const SizedBox(width: 6),
          Text(label),
        ],
      ),
    );
  }
}

class _PreferenceRow extends StatelessWidget {
  final IconData icon;
  final String text;

  const _PreferenceRow({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Colors.indigo),
        const SizedBox(width: 10),
        Expanded(child: Text(text)),
      ],
    );
  }
}

class _TaskPlanTile extends StatelessWidget {
  final AiScheduledTask task;

  const _TaskPlanTile(this.task);

  @override
  Widget build(BuildContext context) {
    final scoreColor = task.priorityScore >= 85
        ? Colors.redAccent
        : task.priorityScore >= 70
        ? Colors.orange
        : Colors.green;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFD),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFD9E3F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFF1F3C88),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${task.startTime} - ${task.endTime}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      task.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(task.client),
                  ],
                ),
              ),
              Chip(
                label: Text(
                  task.priorityScore.toStringAsFixed(0),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                backgroundColor: scoreColor,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(task.address),
          const SizedBox(height: 6),
          Text(
            'Contrato: ${task.contractType}',
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            task.reason,
            style: const TextStyle(color: Colors.black54),
          ),
        ],
      ),
    );
  }
}
