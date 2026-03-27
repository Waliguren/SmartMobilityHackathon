# Smart Mobility Hackathon - Sistema de Gestión de Mantenimiento de Cargadores

## Descripción del Proyecto

**Smart Mobility** es una plataforma integral para la gestión operativa de técnicos de campo especializados en la instalación, mantenimiento y resolución de incidencias de cargadores de coches eléctricos. El sistema permite a los gestores planificar rutas, asignar tareas a técnicos, visualizar el estado de las operaciones en tiempo real mediante un mapa interactivo, y aprovechar algoritmos de optimización y herramientas de IA para mejorar la eficiencia operativa.

El proyecto está desarrollado como parte de un hackathon y abarca tres superficies principales: una aplicación web de gestión, una aplicación móvil para técnicos ya funcional como demo operativa y un backend que integra bases de datos relacionales con servicios en la nube.

---

## Estado del Proyecto

| Componente | Estado | Tecnología |
|------------|--------|------------|
| **Web de Gestión** | ✅ Completado | Flask + SQLite/PostgreSQL |
| **App Móvil Técnicos** | ✅ Demo funcional | Flutter + Firebase |
| **Backend API** | ✅ Funcional | FastAPI + SQLAlchemy |
| **Base de Datos** | ✅ Operativa | PostgreSQL + Firebase Firestore |
| **Motor de IA** | ✅ Implementado | Groq/Llama + VRP Optimizer |

---

## Funcionalidades Implementadas

### 1. Autenticación y Seguridad

- Sistema de login con autenticación de usuarios
- Gestión de sesiones con Flask-Login
- Hash de contraseñas con Bcrypt
- Control de acceso por roles (gestor, técnico, administrador)

### 2. Dashboard Principal

- Métricas operativas en tiempo real:
  - Tareas pendientes totales
  - Riesgos SLA activos
  - Técnicos activos por zona
- Tabla de tareas recientes sin asignar
- Acceso rápido a las principales funcionalidades

### 3. Panel de Control

- Estadísticas visuales con iconos interactivos
- Listado de tareas críticas priorizadas
- Gráficos de progreso de carga de trabajo por zona
- Resumen operativo del día

### 4. Gestión de Tareas/Visitas

- Listado completo con filtros avanzados:
  - Filtrar por tipo (Incidencia, Mantenimiento, Puesta en marcha)
  - Filtrar por zona geográfica
  - Filtrar por prioridad (Alta, Media, Baja)
  - Filtrar por estado (Pendiente, Asignada, Completada)
- Pestañas de navegación: Pendientes, Asignadas, Completadas
- Vista de detalle de cada tarea con toda la información asociada
- Recomendaciones automáticas de asignación

### 5. Asistente de Asignación Inteligente

El componente más avanzado del sistema, que incluye:

- **Panel de carga de trabajo**: Muestra la ocupación actual de cada técnico calculada a partir de tareas asignadas en la base de datos
- **Panel de tareas pendientes**: Lista todas las tareas sin asignar
- **Generación de recomendaciones**: Botón para generar asignaciones automáticas usando el algoritmo VRP
- **Recomendaciones IA**: Al hacer clic en una tarea, se muestra una recomendación de la IA con explicación detallada
- **Edición de asignaciones**: Posibilidad de modificar el técnico asignado y la prioridad
- **Aplicación masiva**: Botón para aplicar todos los cambios pendientes de una vez
- **Actualización en tiempo real**: Después de aplicar cambios, los datos se recargan desde la base de datos

**Algoritmo VRP (Vehicle Routing Problem)**:
El sistema utiliza un algoritmo de puntuación ponderada que considera:
- Distancia geográfica (30%)
- Carga de trabajo actual del técnico (25%)
- Zona del técnico (25%)
- Cumplimiento de SLA (20%)

### 6. Gestión de Técnicos

- Listado de técnicos con buscador por nombre
- Filtros por zona y estado de disponibilidad
- Tarjetas informativas con avatares
- Vista de detalle con:
  - Información completa del técnico
  - Tareas asignadas para el día
  - Estadísticas mensuales de trabajo

### 7. Sistema de Riesgos SLA

- Monitorización de riesgos por incumplimiento de SLA
- Listado filtrable por nivel de riesgo
- Detalle de cada riesgo con información de SLA
- Alertas visuales para tareas críticas

### 8. Mapa Operativo

- Mapa interactivo de España utilizando Leaflet + OpenStreetMap
- Marcadores visuales diferenciados por tipo de tarea:
  - 🔴 Incidencia/Avería
  - 🔵 Mantenimiento preventivo
  - 🟢 Puesta en marcha/Nueva instalación
- Sistema de filtros:
  - Filtrar por tipo de tarea
  - Filtrar por estado (Por asignar, Asignada, Resuelta)
  - Filtrar por técnico asignado
- Información emergente (popup) al hacer clic en cada marcador
- Integración de datos tanto de PostgreSQL como de Firebase Firestore
- Muestra todas las tareas incluyendo las pendientes de asignar

### 9. App móvil para técnicos

La app móvil `technician-mobile` ya cubre el flujo básico del técnico en campo:

- Login demo contra la colección `technicians` de Firestore
- Home con accesos rápidos a mapa, agenda, perfil y AI-Assistant
- Agenda de tareas activas (`pendent`, `en_curs`) desde `visits`
- Detalle de tarea con mapa, ruta OSRM y apertura de Google Maps
- Perfil técnico con métricas básicas y acceso a la agenda completa
- AI-Assistant con botón `Planificador IA`
- Integración con el backend `POST /api/v1/planning/ai-weekly-plan` para generar una propuesta semanal priorizada por criticidad, SLA y valor de cliente

La app móvil usa Firebase Firestore para datos operativos, `flutter_map` para mapas y un backend FastAPI para el planning semanal IA.

---

## Arquitectura Técnica

### Estructura del Proyecto

```
SmartMobilityHackathon/
├── apps/
│   ├── manager-web/                    # Aplicación Flask
│   │   ├── src/
│   │   │   ├── routes/                # Blueprints de Flask
│   │   │   │   ├── auth.py            # Autenticación
│   │   │   │   ├── main.py            # Dashboard y panel
│   │   │   │   ├── tareas.py          # Gestión de tareas
│   │   │   │   ├── tecnicos.py        # Gestión de técnicos
│   │   │   │   ├── riesgos.py         # Riesgos SLA
│   │   │   │   ├── mapa.py            # Mapa operativo
│   │   │   │   └── asignacion.py      # Asistente de asignación
│   │   │   ├── services/              # Servicios de negocio
│   │   │   │   ├── firebase_service.py # Integración Firestore
│   │   │   │   ├── vrp_optimizer.py    # Algoritmo de optimización
│   │   │   │   ├── ia_explicacion.py  # Servicio de IA
│   │   │   │   └── geocoding.py       # Geocodificación
│   │   │   ├── models/                 # Modelos SQLAlchemy
│   │   │   │   ├── user.py             # Modelo de usuario
│   │   │   │   └── operations.py      # Modelos operativos
│   │   │   ├── templates/              # Plantillas HTML
│   │   │   │   ├── base.html          # Plantilla base
│   │   │   │   ├── dashboard.html
│   │   │   │   ├── panel.html
│   │   │   │   ├── asignacion.html
│   │   │   │   ├── mapa.html
│   │   │   │   └── auth/
│   │   │   └── static/                 # Recursos estáticos
│   │   ├── config.py                   # Configuración
│   │   ├── run.py                       # Punto de entrada
│   │   └── requirements.txt
│   └── technician-mobile/              # App Flutter para técnicos
├── backend/
│   ├── api/                           # FastAPI
│   ├── firebase/                      # Firebase Functions
│   └── postgres/                      # PostgreSQL + PostGIS
├── docs/                              # Documentación técnica
├── docker-compose.yml                 # Orquestación Docker
├── .env.example                       # Variables de entorno ejemplo
└── README.md
```

### Stack Tecnológico

| Capa | Tecnología | Versión |
|------|------------|---------|
| **Frontend Web** | Flask + Jinja2 | Flask 3.x |
| **Frontend Móvil** | Flutter | SDK 3.11+ |
| **Frontend JS** | Vanilla JavaScript | - |
| **Mapas** | Leaflet + OpenStreetMap | - |
| **Backend** | FastAPI + SQLAlchemy | Python 3.12+ |
| **Base de Datos 1** | PostgreSQL + PostGIS | 16+ |
| **Base de Datos 2** | Firebase Firestore | - |
| **Autenticación** | Flask-Login + Bcrypt | - |
| **IA** | Groq API (Llama 3.1) | - |
| **Contenedores** | Docker + Docker Compose | - |

### Modelo de Datos

El sistema opera con dos fuentes de datos complementarias:

**PostgreSQL (Núcleo transaccional)**:
- `Users`: Usuarios del sistema
- `Technicians`: Técnicos de campo
- `Contracts`: Contratos con clientes
- `Visits`: Visitas/tareas planificadas
- `Incidences`: Incidencias registradas
- `Reports`: Informes de intervenciones

**Firebase Firestore (Datos operativos)**:
- `visits`: Tareas pendientes y en proceso
- `technicians`: Información de técnicos
- `incidences`: Incidencias activas
- `contracts`: Datos de contratos

### Flujo de Datos

1. Las tareas se originan en sistemas externos y se almacenan en Firebase Firestore
2. El dashboard de gestión lee de ambas bases de datos
3. Las asignaciones se guardan en Firebase actualizando el campo `technician_id`
4. La app móvil lee `technicians`, `visits`, `incidences` y `contracts` desde Firestore
5. El AI-Assistant móvil agrega esos datos y llama al backend FastAPI para obtener el planning semanal IA
6. El mapa integra datos de ambas fuentes para mostrar el estado completo

---

## Instalación y Configuración

### Requisitos Previos

- Python 3.12 o superior
- Node.js 20+ (opcional, para desarrollo frontend)
- PostgreSQL 16+ con extensión PostGIS
- Docker Desktop (recomendado para desarrollo rápido)
- Firebase CLI (para configuración de Firestore)

### Configuración con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
cd SmartMobilityHackathon

# 2. Copiar archivo de variables de entorno
cp .env.example .env

# 3. Iniciar servicios con Docker
docker compose up --build

# 4. Acceder a la aplicación
# Web: http://localhost:5000
```

### Configuración Manual

```bash
# 1. Instalar dependencias Python
cd apps/manager-web
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp ../../.env.example .env
# Editar .env con tus valores

# 3. Inicializar base de datos
python -c "from src import create_app, db; app = create_app(); db.create_all()"

# 4. Iniciar servidor
python run.py
# La aplicación estará disponible en http://localhost:5000
```

### App móvil Flutter

La app móvil vive en `apps/technician-mobile` y actualmente funciona como cliente operativo de demo.

```bash
cd apps/technician-mobile
flutter pub get
flutter run
```

Si necesitas apuntar el planificador IA a otra URL del backend:

```bash
flutter run --dart-define=FLUTTER_API_BASE_URL=http://localhost:8000
```

Notas útiles:

- En emulador Android, `10.0.2.2` apunta al host local.
- En dispositivo físico, hay que usar la IP real de la máquina donde corre el backend.

### Credenciales de Acceso

Por defecto, el sistema utiliza un usuario hardcodeado para desarrollo:

- **Email**: admin@smartmobility.com
- **Contraseña**: admin123

**Nota**: En producción, esto debe configurarse correctamente con usuarios en la base de datos.

### Configuración de Firebase

Para conectar con Firebase Firestore:

1. Obtener las credenciales del proyecto Firebase
2. Colocar el archivo `privateKey_firebase.json` en la raíz del proyecto
3. Configurar las variables de entorno en `.env`:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - Etc.

La app móvil Android ya incluye `google-services.json`, pero sigue dependiendo de que Firebase esté correctamente configurado para la plataforma donde se ejecute.

### Configuración de IA (Groq)

Para habilitar las explicaciones de IA:

1. Obtener una API key de [Groq](https://groq.com)
2. Añadir la variable de entorno:
   ```
   GROQ_API_KEY=tu_api_key_aqui
   ```

La app móvil no llama directamente a Groq. El consumo de IA se realiza a través del backend FastAPI.

---

## Uso del Sistema

### Flujo de Trabajo Típico

1. **Inicio de sesión**: El gestor accede con sus credenciales
2. **Revisión del dashboard**: Observa métricas y tareas pendientes
3. **Acceso al mapa**: Visualiza la distribución geográfica de tareas
4. **Asistente de asignación**:
   - Observa la carga de trabajo de cada técnico
   - Selecciona tareas pendientes
   - Genera recomendaciones automáticas
   - Revisa y ajusta asignaciones si es necesario
   - Aplica los cambios
5. **Seguimiento**: Monitoriza el estado en el mapa

### Tipos de Tareas

| Tipo | Color | Descripción |
|------|-------|-------------|
| **Incidencia** | 🔴 Rojo | Problemas, averías, fallos urgentes |
| **Mantenimiento** | 🔵 Azul | Mantenimiento preventivo programado |
| **Puesta en Marcha** | 🟢 Verde | Nueva instalación de cargador |

### Estados de Tareas

| Estado | Descripción |
|--------|-------------|
| **Pendiente** | Tarea creada, sin asignar |
| **En Proceso** | Asignada a un técnico |
| **Asignada** | Confirmada la asignación |
| **Completada** | Tarea finalizada |

---

## API Endpoints

### Autenticación

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/login` | Página de login |
| POST | `/login` | Proceso de autenticación |
| GET | `/logout` | Cierre de sesión |

### Dashboard y Panel

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard` | Dashboard principal |
| GET | `/panel` | Panel de control operativo |

### Tareas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tareas` | Listado de tareas con filtros |
| GET | `/tareas/<id>` | Detalle de una tarea |

### Técnicos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tecnicos` | Listado de técnicos |
| GET | `/tecnicos/<id>` | Detalle de un técnico |

### Riesgos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/riesgos` | Listado de riesgos SLA |
| GET | `/riesgos/<id>` | Detalle de un riesgo |

### Mapa

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/mapa` | Vista del mapa operativo |
| GET | `/api/tareas-mapa` | API de tareas para el mapa |

### Backend de planificación consumido por la app móvil

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/planning/ai-weekly-plan` | Genera un planning semanal IA para el técnico móvil |

### Asistente de Asignación

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/asignacion` | Vista del asistente |
| GET | `/api/asignacion/datos` | Datos de técnicos y tareas |
| POST | `/api/asignacion/recomendar` | Recomendaciones VRP |
| POST | `/api/asignacion/sugerir-ia` | Sugerencias con IA |
| POST | `/api/asignacion/recomendar-una` | Recomendación para una tarea |
| POST | `/api/asignacion/generar` | Generación masiva |
| POST | `/api/asignacion/corregir` | Corrección de asignación |
| POST | `/api/asignacion/aplicar` | Aplicar cambios |

---

## Servicios de Inteligencia Artificial

### VRP Optimizer (`vrp_optimizer.py`)

Implementa un algoritmo de optimización de rutas y asignación que considera múltiples factores:

- **Distancia geográfica**: Usando la fórmula Haversine para calcular distancias entre coordenadas
- **Carga de trabajo**: Número actual de tareas asignadas al técnico
- **Zona del técnico**: Preferencia por asignar en la zona asignada
- **SLA**: Prioridad por cumplir tiempos de servicio

### IA Explicación (`ia_explicacion.py`)

Servicio que genera explicaciones naturales para las recomendaciones:

- Análisis de factores que influyen en la asignación
- Generación de texto explicativo en español
- Preparado para integración con Groq/Llama para explicaciones más naturales
- Sistema de autoaprendizaje mediante almacenamiento de correcciones

---

## Desarrollo y Contribución

### Estructura de Ramas

- `main`: Rama principal de producción
- `manager-web`: Desarrollo de la aplicación web

### Convenciones de Código

- Python: PEP 8 con type hints
- HTML/Jinja2: Plantillas con Bootstrap 5
- JavaScript: Vanilla JS con sintaxis moderna
- CSS: Bootstrap integrado

### Ejecutar Tests

```bash
# Tests unitarios (pendiente de implementar)
cd apps/manager-web
pytest
```

### Construir para Producción

```bash
# Docker
docker build -t smartmobility-web ./apps/manager-web
docker run -p 5000:5000 smartmobility-web
```

---

## Documentación Adicional

| Documento | Descripción |
|-----------|-------------|
| `docs/ARCHITECTURE.md` | Arquitectura técnica detallada |
| `docs/DATA_MODEL.md` | Modelo de datos y criterios de persistencia |
| `docs/PLANNING_ENGINE.md` | Diseño del motor de planificación |
| `docs/PRODUCT_SCOPE.md` | Alcance funcional del MVP |
| `docs/DEVELOPMENT.md` | Convenciones y siguientes pasos |
| `CONTEXTO_PROYECTO.md` | Contexto histórico del proyecto |

---

## Limitaciones y Trabajo Futuro

### Completado ✅

- Sistema de autenticación funcional
- Dashboard y panel de control operativos
- Gestión completa de tareas con filtros
- Mapa interactivo con datos de Firebase
- Asistente de asignación con algoritmo VRP
- Integración con Firebase Firestore

### Pendiente 🔄

- Endurecer la app Flutter para uso menos demo y más estable
- Integración real con Groq API para explicaciones avanzadas y refinamiento del planning
- Sistema de autoaprendizaje (guardar correcciones del usuario)
- Sincronización offline para la app móvil
- Integración con OpenChargeMap
- Integración con Google Cloud Fleet Routing
- Informes y analíticas avanzadas
- Notificaciones en tiempo real

---

## Licencia

Este proyecto fue desarrollado como parte del Hackathon SmartMobility. Ver archivo `Enunciat Hackató SmAIrt Mobility.pdf` para más detalles sobre los requisitos originales.

---

## Contacto y Soporte

Para preguntas o problemas con el proyecto, por favor contactar con el equipo de desarrollo o abrir un issue en el repositorio.

**Versión actual**: 1.0.0
**Última actualización**: Marzo 2026
