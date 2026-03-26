# Arquitectura Inicial

## Resumen

La solución se organiza como monorepo con tres piezas principales:

- `apps/manager-web`: interfaz para gestores operativos
- `apps/technician-mobile`: app Flutter para técnicos e instaladores
- `backend/api`: API central para reglas de negocio, persistencia y planificación

La base operativa principal pasa a ser PostgreSQL/PostGIS. Firebase queda como plataforma complementaria para:

- autenticación
- persistencia documental ligera en escenarios concretos
- almacenamiento de evidencias
- posibles notificaciones y extensiones futuras

## Diagrama de alto nivel

```text
┌──────────────────────┐         ┌──────────────────────┐
│  Web gestores        │         │  App técnicos        │
│  React + Vite        │         │  Flutter             │
└──────────┬───────────┘         └──────────┬───────────┘
           │ HTTP/JSON                       │ HTTP/JSON
           └──────────────┬──────────────────┘
                          ▼
                 ┌──────────────────────┐
                 │  Backend API         │
                 │  FastAPI + Uvicorn   │
                 └───────┬───────┬──────┬──────────────────────┐
                         │       │      │                      │
                         ▼       ▼      ▼                      ▼
                ┌─────────────┐  ┌───────────────┐   ┌──────────────────┐
                │ PostgreSQL  │  │ Planning      │   │ Firebase Auth /  │
                │ + PostGIS   │  │ Engine        │   │ Storage          │
                └─────────────┘  └──────┬────────┘   └──────────────────┘
                                        │
                           ┌────────────┴────────────┐
                           ▼                         ▼
                 ┌──────────────────┐      ┌───────────────────────┐
                 │ OpenChargeMap    │      │ Google Fleet Routing  │
                 └──────────────────┘      └───────────────────────┘
```

## Modelo de dominio inicial

Entidades base tomadas del ERD y ampliadas para la operativa real:

- `Client`: cliente propietario o gestor de cargadores
- `Charger`: punto de recarga geolocalizado
- `Contract`: acuerdos de mantenimiento preventivo
- `Incidence`: eventos correctivos o incidencias abiertas
- `Technician`: técnico o instalador asignable
- `Visit`: unidad operativa ejecutable en campo
- `RoutePlan`: planificación semanal por técnico
- `RouteStop`: secuencia de visitas dentro de un plan
- `Report`: resultado de una visita

Relaciones clave:

- Un cliente puede tener múltiples cargadores y contratos
- Un contrato puede generar múltiples visitas
- Una incidencia puede generar o materializar una visita correctiva
- Un técnico puede estar asignado a múltiples visitas y múltiples planes semanales
- Un plan semanal contiene una secuencia ordenada de paradas
- Una visita puede producir un reporte

## Por qué no Firebase como base principal

Para el caso de uso confirmado hay cuatro necesidades que no conviene resolver sobre Firestore:

- consultas transaccionales y relacionales entre contratos, cargadores, incidencias, técnicos y visitas
- filtrado geográfico y cálculo de vecindad a escala nacional
- planificación semanal con restricciones y estados consistentes
- explotación analítica de asignaciones y rutas

Por eso la arquitectura recomendada es híbrida:

- PostgreSQL/PostGIS: sistema operacional principal
- FastAPI: capa de dominio, planificación e integraciones
- Firebase: autenticación, storage y soporte app móvil

## Módulos previstos en backend

- `auth`: autenticación y autorización por roles
- `clients`: datos del cliente y criticidad contractual
- `chargers`: inventario de cargadores y geolocalización
- `contracts`: gestión de contratos y periodicidades
- `incidences`: creación y seguimiento de incidencias
- `technicians`: técnicos, zonas y disponibilidad
- `visits`: planificación, asignación y estados de visita
- `planning`: scoring heurístico, planificación semanal y secuenciación de rutas
- `reports`: reportes de ejecución y evidencias
- `integrations`: OpenChargeMap y Google Fleet Routing
- `media`: almacenamiento de fotos y archivos
- `shared`: modelos comunes, validaciones y utilidades

## Módulos previstos en la web de gestores

- `dashboard`
- `contracts`
- `incidences`
- `visits`
- `reports`
- `technicians`
- `map`

## Módulos previstos en la app móvil

- `auth`
- `assigned_visits`
- `visit_execution`
- `report_capture`
- `offline_sync`

## Decisiones no cerradas todavía

- Estrategia exacta de sincronización offline
- Umbral exacto de zona razonable entre técnico y cargador
- Si la planificación automática se ejecutará síncrona bajo demanda o como job asíncrono
- Uso final de Google Fleet Routing como motor principal o como optimizador secundario
- Modelo definitivo de archivos multimedia y tamaño de evidencias
- Reglas de seguridad finales en Firebase Auth y Storage

## Convención de despliegue inicial

- Desarrollo local: `docker-compose.yml` para web, backend y PostgreSQL/PostGIS
- Mobile: ejecución directa con `flutter run`
- Entornos previstos: `dev`, `staging`, `prod`