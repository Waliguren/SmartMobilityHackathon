class Technician {
  final String id;
  final String name;
  final String zone;
  final int expertise;
  final bool expert;

  const Technician({
    required this.id,
    required this.name,
    required this.zone,
    required this.expertise,
    required this.expert,
  });

  factory Technician.fromFirestore(Map<String, dynamic> data, String docId) {
    return Technician(
      id: docId,
      name: (data['name'] ?? '').toString(),
      zone: (data['zone'] ?? '').toString(),
      expertise: (data['expertise'] ?? 0) as int,
      expert: (data['expert'] ?? false) as bool,
    );
  }
}
