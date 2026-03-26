# Arquitectura Inicial

## Resumen

La solución se organiza como monorepo con tres piezas principales:

- `apps/manager-web`: interfaz para gestores operativos
- `apps/technician-mobile`: app Flutter para técnicos e instaladores
- `backend/api`: API central para reglas de negocio e integración con Firebase

Firebase queda como backend gestionado para:

- autenticación
- persistencia documental
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
                 └───────┬───────┬──────┘
                         │       │
                         │       └──────────────────────┐
                         ▼                              ▼
                ┌──────────────────┐          ┌──────────────────┐
                │ Firebase Auth    │          │ Firestore /      │
                │ Roles y sesiones │          │ Storage          │
                └──────────────────┘          └──────────────────┘
```

## Modelo de dominio inicial

Entidades base tomadas del ERD:

- `Contract`: acuerdos de mantenimiento preventivo
- `Incidence`: eventos correctivos o incidencias abiertas
- `Technician`: técnico o instalador asignable
- `Visit`: unidad operativa ejecutable en campo
- `Report`: resultado de una visita

Relaciones clave:

- Un contrato puede generar múltiples visitas
- Una incidencia puede generar una visita correctiva
- Un técnico puede estar asignado a múltiples visitas
- Una visita puede producir un reporte

## Módulos previstos en backend

- `auth`: autenticación y autorización por roles
- `contracts`: gestión de contratos y periodicidades
- `incidences`: creación y seguimiento de incidencias
- `visits`: planificación, asignación y estados de visita
- `reports`: reportes de ejecución y evidencias
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
- Si la planificación automática vivirá en FastAPI, jobs externos o Cloud Functions
- Modelo definitivo de archivos multimedia y tamaño de evidencias
- Reglas de seguridad finales en Firestore y Storage

## Convención de despliegue inicial

- Desarrollo local: `docker-compose.yml` para web y backend
- Mobile: ejecución directa con `flutter run`
- Entornos previstos: `dev`, `staging`, `prod`