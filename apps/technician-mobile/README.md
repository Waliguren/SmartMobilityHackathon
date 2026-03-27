# Technician Mobile

App Flutter para técnicos de campo de SmAIrt Mobility. La aplicación permite iniciar sesión, consultar tareas asignadas, revisar detalle de visitas con navegación, ver perfil técnico y generar una propuesta semanal con apoyo del backend de planificación IA.

## Objetivo

La app está pensada como interfaz operativa móvil para el técnico que trabaja sobre estaciones de carga. Su foco actual es:

- Consultar tareas pendientes y en curso.
- Ver la localización de una visita y abrir navegación.
- Revisar información del técnico y volumen de trabajo.
- Pedir al backend una propuesta semanal priorizada por criticidad, SLA y valor de cliente.

## Estado actual

La app está funcional como demo de hackathon y se apoya en Firebase Firestore para datos operativos y en el backend FastAPI del repositorio para la generación del planning IA.

Puntos relevantes del estado actual:

- El login valida usuarios contra la colección `technicians`.
- La contraseña demo está fijada en `1234` y se compara por hash SHA-256 en cliente.
- Las tareas se leen desde Firestore, principalmente de la colección `visits`.
- El planificador IA envía datos agregados al endpoint `POST /api/v1/planning/ai-weekly-plan`.
- La app usa `flutter_map` con OpenStreetMap y consume rutas desde OSRM público.

## Funcionalidades

### 1. Login

Archivo principal: [lib/main.dart](./lib/main.dart)

- Inicializa Firebase con `Firebase.initializeApp()`.
- Busca el técnico por nombre en `technicians`.
- Guarda el técnico autenticado en la variable global `loggedTechnician`.

### 2. Home

Archivo: [lib/screens/home_screen.dart](./lib/screens/home_screen.dart)

- Pantalla de bienvenida con imagen de fondo.
- Barra inferior con accesos rápidos a:
  - mapa
  - agenda
  - perfil
  - AI-Assistant

### 3. Agenda

Archivo: [lib/screens/agenda_screen.dart](./lib/screens/agenda_screen.dart)

- Escucha en tiempo real la colección `visits`.
- Filtra tareas por técnico y por estado (`pendent`, `en_curs`) cuando procede.
- Muestra prioridad operativa, estado, tiempo estimado y destino.
- Permite abrir el detalle de la tarea.

### 4. Detalle de tarea

Archivo: [lib/screens/task_detail_screen.dart](./lib/screens/task_detail_screen.dart)

- Obtiene posición actual del técnico con `geolocator`.
- Dibuja mapa y ruta entre origen y destino.
- Usa OSRM para calcular la ruta.
- Permite abrir Google Maps en navegación externa.

### 5. Mapa

Archivo: [lib/screens/map_screen.dart](./lib/screens/map_screen.dart)

- Muestra la posición actual del técnico.
- Permite tocar sobre el mapa para fijar un destino manual.
- Calcula una ruta de prueba usando OSRM.

### 6. Perfil

Archivo: [lib/screens/profile_screen.dart](./lib/screens/profile_screen.dart)

- Muestra nombre, zona, experiencia y si el técnico es especialista.
- Calcula cuántas tareas activas tiene el técnico.
- Permite abrir la agenda completa del técnico.

### 7. AI-Assistant

Archivos:

- [lib/screens/others_screen.dart](./lib/screens/others_screen.dart)
- [lib/services/ai_assistant_service.dart](./lib/services/ai_assistant_service.dart)
- [lib/models/ai_weekly_plan.dart](./lib/models/ai_weekly_plan.dart)

Qué hace:

- Recoge visitas activas del técnico.
- Enriqueca cada visita con datos de `incidences` y `contracts`.
- Envía el lote al backend de planificación IA.
- Recibe un planning semanal ya ordenado por días y horas.
- Lo presenta por columnas temporales de lunes a viernes.

La UI mantiene el naming `Planificador IA` y la etiqueta visual `AI-Generated`.

## Arquitectura funcional

### Fuentes de datos

La app trabaja con estas colecciones de Firestore:

- `technicians`
- `visits`
- `incidences`
- `contracts`

Relación usada por la app:

1. `visits` aporta la tarea asignada al técnico.
2. `incidences` amplía la prioridad y descripción usando `incidence_id`.
3. `contracts` amplía cliente y tipo de contrato usando `charger_id`.

### Backend externo usado por la app

El planificador IA no se resuelve localmente en Flutter. La app llama a:

`POST /api/v1/planning/ai-weekly-plan`

Base URL configurada:

- Por defecto: `http://10.0.2.2:8000`
- Se puede sobrescribir con `--dart-define=FLUTTER_API_BASE_URL=...`

### Navegación

Rutas definidas en `MaterialApp`:

- `/home`
- `/map`
- `/agenda`
- `/profile`
- `/ai-assistant`

## Estructura del proyecto

```text
apps/technician-mobile/
├─ android/
├─ assets/
│  └─ fondo.png
├─ lib/
│  ├─ models/
│  │  ├─ ai_weekly_plan.dart
│  │  ├─ task.dart
│  │  └─ technician.dart
│  ├─ screens/
│  │  ├─ agenda_screen.dart
│  │  ├─ home_screen.dart
│  │  ├─ map_screen.dart
│  │  ├─ others_screen.dart
│  │  ├─ profile_screen.dart
│  │  └─ task_detail_screen.dart
│  ├─ services/
│  │  └─ ai_assistant_service.dart
│  └─ main.dart
├─ pubspec.yaml
└─ README.md
```

## Dependencias principales

Definidas en [pubspec.yaml](./pubspec.yaml):

- `firebase_core`: inicialización de Firebase
- `cloud_firestore`: acceso a Firestore
- `http`: llamadas HTTP al backend IA y a OSRM
- `flutter_map`: renderizado de mapas
- `latlong2`: coordenadas geográficas
- `geolocator`: ubicación del dispositivo
- `url_launcher`: apertura de Google Maps
- `crypto`: hash de contraseña demo

## Requisitos

Antes de arrancar la app necesitas:

- Flutter instalado
- SDK/entorno Android o emulador operativo
- Firebase configurado para la app
- Backend API arrancado si quieres usar el planificador IA

## Configuración de Firebase

En Android ya existe un archivo:

- [android/app/google-services.json](./android/app/google-services.json)

Además, la app espera que `Firebase.initializeApp()` funcione al arrancar, así que cualquier plataforma adicional debe estar correctamente configurada.

## Cómo arrancar la app

Desde la raíz del repositorio:

```powershell
cd apps/technician-mobile
flutter pub get
flutter run
```

Si quieres apuntar al backend en otra URL:

```powershell
flutter run --dart-define=FLUTTER_API_BASE_URL=http://localhost:8000
```

Nota para emulador Android:

- `10.0.2.2` es correcto para llegar al host local desde el emulador.

Nota para dispositivo físico:

- Sustituye la URL por la IP real de tu máquina en la red local.

## Cómo arrancar el backend para el planificador IA

Desde la raíz del repositorio, en otra terminal:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
    $name = $matches[1]
    $value = $matches[2].Trim().Trim('"')
    Set-Item -Path "Env:$name" -Value $value
  }
}

& .\backend\api\.venv\Scripts\Activate.ps1
cd .\backend\api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints útiles:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Planning IA: `http://localhost:8000/api/v1/planning/ai-weekly-plan`

## Modelo de datos en la app

### Technician

Archivo: [lib/models/technician.dart](./lib/models/technician.dart)

Campos usados:

- `id`
- `name`
- `zone`
- `expertise`
- `expert`

### Task

Archivo: [lib/models/task.dart](./lib/models/task.dart)

Campos usados:

- `id`
- `titulo`
- `prioridad`
- `tiempoEstimado`
- `destino`
- `destinoCoords`
- `status`
- `incidenceId`
- `technicianId`

### AiWeeklyPlan

Archivo: [lib/models/ai_weekly_plan.dart](./lib/models/ai_weekly_plan.dart)

Representa la respuesta del backend:

- `engine`
- `summary`
- `usedFallback`
- `preferencesAssumed`
- `scheduledTasks`

## Flujo del planificador IA

1. El técnico inicia sesión.
2. Entra en `AI-Assistant`.
3. Pulsa `Planificador IA`.
4. La app recopila tareas activas del técnico desde Firestore.
5. Enriquece los datos con prioridad, cliente y contrato.
6. Envía el payload al backend IA.
7. El backend devuelve un planning semanal ordenado.
8. La app renderiza el resultado por día.

## Consideraciones importantes

### Seguridad

El login actual es solo de demo:

- la contraseña está fija en cliente
- no hay autenticación real contra backend
- no hay sesión persistente segura

No debe tratarse como un diseño de producción.

### Red y servicios externos

La app depende de:

- Firestore para datos
- backend FastAPI para planning IA
- OSRM público para rutas
- Google Maps opcional para navegación externa

Si cualquiera de esos servicios no está disponible, parte de la experiencia dejará de funcionar.

### Limitaciones conocidas

- No hay gestión real de estados offline.
- No hay refresh token ni autenticación robusta.
- La contraseña demo está embebida en la app.
- La configuración de Firebase no está descrita para todas las plataformas.
- El planificador IA depende de que el backend esté activo y accesible desde el dispositivo.

## Desarrollo recomendado

Si vas a tocar esta app, los mejores puntos de entrada son:

- [lib/main.dart](./lib/main.dart) para arranque y routing
- [lib/screens/agenda_screen.dart](./lib/screens/agenda_screen.dart) para tareas
- [lib/screens/task_detail_screen.dart](./lib/screens/task_detail_screen.dart) para navegación y mapas
- [lib/screens/others_screen.dart](./lib/screens/others_screen.dart) para UX del planificador
- [lib/services/ai_assistant_service.dart](./lib/services/ai_assistant_service.dart) para integración con backend

## Próximos pasos sugeridos

- Sustituir el login demo por autenticación real.
- Centralizar estado de sesión y técnico autenticado.
- Añadir manejo de errores de red más fino.
- Añadir pruebas widget/integración para login, agenda y AI-Assistant.
- Formalizar configuración multiplataforma de Firebase.
- Añadir indicadores de carga y estados vacíos más ricos.

## Comandos útiles

```powershell
flutter pub get
flutter analyze
flutter test
flutter run
```
