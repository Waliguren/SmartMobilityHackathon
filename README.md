# Smart Mobility Hackathon

Base inicial del nuevo proyecto de hackathon para la operativa de mantenimiento de cargadores.

Estado actual:

- Monorepo inicial creado
- Decisiones técnicas base documentadas
- Estructura preparada para frontend web de gestores, app móvil de técnicos en Flutter y backend FastAPI
- Backend reorientado a planificación geográfica semanal sobre PostgreSQL/PostGIS
- Firebase queda como soporte complementario para auth, storage y sincronización futura

## Objetivo

Construir una plataforma con tres superficies principales:

- Web de gestores para planificar contratos, incidencias, visitas y revisar reportes
- App móvil para técnicos/instaladores con agenda, ejecución de visitas y captura de reportes
- Backend API para autenticación, planificación operativa y persistencia transaccional/geográfica

## Contexto funcional actual

El dominio base parte del ERD incluido en el repositorio:

- `CONTRACT` genera visitas planificadas
- `INCIDENCE` puede disparar visitas correctivas
- `TECHNICIAN` recibe asignaciones por zona y carga operativa
- `VISIT` concentra la operación de campo
- `REPORT` recoge el resultado de la intervención

El escenario operativo confirmado ahora es más exigente:

- unos 17K cargadores distribuidos por España
- múltiples incidencias abiertas el mismo día
- planificación semanal por técnico
- prioridad combinada por SLA, impacto cliente y urgencia
- optimización de ruta sobre red viaria
- integración con OpenChargeMap y Google Cloud Fleet Routing

## Decisiones iniciales

- `apps/manager-web`: React + Vite + TypeScript
- `apps/technician-mobile`: Flutter
- `backend/api`: FastAPI + Uvicorn
- `backend/postgres`: PostgreSQL/PostGIS para operación y optimización
- `backend/firebase`: Firebase Auth/Storage como complemento
- `docker-compose.yml`: arranque local de web, backend y PostgreSQL

La decisión relevante tras la reunión de arquitectura es esta: Firebase no debe ser la base operativa principal para el planificador. Para consultas transaccionales, asignación semanal, ordenación por heurística y trabajo geoespacial, la base correcta es PostgreSQL con extensión PostGIS. Firebase sigue siendo útil, pero no como núcleo de planificación.

## Estructura

```text
SmartMobilityHackathon/
├── apps/
│   ├── manager-web/
│   └── technician-mobile/
├── backend/
│   ├── api/
│   ├── firebase/
│   └── postgres/
├── docs/
├── .editorconfig
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Enunciat Hackató SmAIrt Mobility.pdf
├── README.md
└── erd_visitas_mantenimiento_mermaid.md
```

## Primer alcance funcional

### Web gestores

- Dashboard operativo
- Vista de contratos
- Gestión de incidencias
- Calendario/listado de visitas
- Asignación de técnicos
- Revisión de reportes
- Mapa operativo y filtros

### App técnicos

- Login
- Lista de visitas asignadas
- Detalle de visita
- Check-in y check-out
- Captura de observaciones, fotos y firma
- Trabajo offline con sincronización diferida

### Backend

- API REST inicial
- Autenticación por roles
- Modelado de clientes, cargadores, contratos, incidencias, visitas, planes de ruta y reportes
- Motor de priorización y planificación semanal
- Soporte para A* sobre grafo viario cargado desde GeoJSON
- Integración preparada con OpenChargeMap
- Integración preparada con Google Fleet Routing
- Base transaccional PostgreSQL/PostGIS
- Firebase como soporte para auth y ficheros

## Arranque local

### Requisitos

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+ con PostGIS
- Flutter 3.29+
- Firebase CLI
- Docker Desktop opcional

### Variables de entorno

Copiar `.env.example` a `.env` y completar valores reales cuando empiece la implementación.

### Desarrollo sin Docker

```bash
# Web gestores
cd apps/manager-web
npm install
npm run dev

# Backend API
cd backend/api
python -m pip install -e .
uvicorn app.main:app --reload

# App móvil
cd apps/technician-mobile
flutter pub get
flutter run
```

### Desarrollo con Docker

```bash
docker compose up --build
```

### Script Windows

Para arrancar en Windows la base de datos, el backend y la web de gestores, sin Flutter:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

## Documentación

- `docs/ARCHITECTURE.md`: arquitectura técnica y flujo entre aplicaciones
- `docs/DATA_MODEL.md`: modelo de datos operativo y criterios de persistencia
- `docs/PLANNING_ENGINE.md`: diseño del motor de planificación semanal
- `docs/PRODUCT_SCOPE.md`: alcance funcional inicial y límites del MVP
- `docs/DEVELOPMENT.md`: convenciones de desarrollo y siguientes pasos

## Nota

Este repositorio ya incluye la primera base del backend y del modelo de datos para el planificador, pero no deja todavía una solución cerrada de producción ni la app móvil funcional.