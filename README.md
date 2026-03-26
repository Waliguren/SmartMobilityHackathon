# Smart Mobility Hackathon

Base inicial del nuevo proyecto de hackathon para la operativa de mantenimiento de cargadores.

Estado actual:

- Monorepo inicial creado
- Decisiones técnicas base documentadas
- Estructura preparada para frontend web de gestores, app móvil de técnicos en Flutter y backend FastAPI con Firebase
- Sin implementación funcional de negocio todavía

## Objetivo

Construir una plataforma con tres superficies principales:

- Web de gestores para planificar contratos, incidencias, visitas y revisar reportes
- App móvil para técnicos/instaladores con agenda, ejecución de visitas y captura de reportes
- Backend API para autenticación, orquestación operativa y persistencia sobre Firebase

## Contexto funcional actual

El dominio base parte del ERD incluido en el repositorio:

- `CONTRACT` genera visitas planificadas
- `INCIDENCE` puede disparar visitas correctivas
- `TECHNICIAN` recibe asignaciones
- `VISIT` concentra la operación de campo
- `REPORT` recoge el resultado de la intervención

## Decisiones iniciales

- `apps/manager-web`: React + Vite + TypeScript
- `apps/technician-mobile`: Flutter
- `backend/api`: FastAPI + Uvicorn
- `backend/firebase`: Firestore, Auth y Storage como base gestionada
- `docker-compose.yml`: arranque local de web y backend para desarrollo

La elección del stack web queda fijada aquí como punto de partida para no bloquear el scaffolding. Si se decide cambiar de framework, la estructura del monorepo sigue siendo válida.

## Estructura

```text
SmartMobilityHackathon/
├── apps/
│   ├── manager-web/
│   └── technician-mobile/
├── backend/
│   ├── api/
│   └── firebase/
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
- Modelado de contratos, incidencias, visitas y reportes
- Integración con Firebase Admin SDK
- Reglas de seguridad y estructura inicial de Firestore

## Arranque local

### Requisitos

- Node.js 20+
- Python 3.12+
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

## Documentación

- `docs/ARCHITECTURE.md`: arquitectura técnica y flujo entre aplicaciones
- `docs/PRODUCT_SCOPE.md`: alcance funcional inicial y límites del MVP
- `docs/DEVELOPMENT.md`: convenciones de desarrollo y siguientes pasos

## Nota

Este commit deja la base del proyecto y la estructura de trabajo. No hay lógica de negocio implementada, ni endpoints de dominio, ni pantallas funcionales.