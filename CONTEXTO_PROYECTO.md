# Contexto del Proyecto - Smart Mobility Hackathon

## Resumen del Proyecto

Sistema de gestión de rutas para técnicos de campo queinstalan, mantienen y resuelven incidencias de cargadores de coches eléctricos.

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **App Web (Operaciones)** | Flask (Python) - EN DESARROLLO |
| **App Móvil (Técnicos)** | Flutter (pendiente) |
| **Backend/IA** | Firebase + Groq (Llama) |
| **Mapas** | Leaflet + OpenStreetMap |

---

## Estructura del Proyecto

```
SmartMobilityHackathon/
├── apps/
│   ├── manager-web/        # App Flask - EN DESARROLLO
│   │   ├── src/
│   │   │   ├── routes/     # auth, main, tareas, tecnicos, riesgos, mapa, asignacion
│   │   │   ├── templates/  # HTML templates
│   │   │   ├── services/   # vrp_optimizer.py, ia_explicacion.py
│   │   │   ├── models/     # User model
│   │   │   └── static/     # CSS, JS
│   │   ├── config.py
│   │   ├── run.py
│   │   └── requirements.txt
│   └── technician-mobile/   # App Flutter - PENDIENTE
├── backend/                 # Firebase Functions - PENDIENTE
├── docker-compose.yml
├── docs/
├── Material Suport Hackato SmAIrt Mobility/
└── CONTEXTO_PROYECTO.md
```

---

## Funcionalidades Implementadas

### App de Escritorio (Operaciones) - COMPLETADO ✅

**1. Login hardcodeado**
- Email: admin@smartmobility.com
- Password: admin123

**2. Dashboard**
- Tarjetas con métricas (Tareas Pendientes, Riesgos SLA, Técnicos Activos)
- Tabla de tareas recientes sin asignar

**3. Panel de Control**
- Estadísticas con iconos (todos clickeables)
- Tareas críticas listadas
- Técnicos por zona (gráficos de progreso)

**4. Gestión de Tareas**
- Lista con filtros (Tipo, Zona, Prioridad)
- Tabs: Pendientes, Asignadas, Completadas

**5. Detalle de Tarea**
- Datos generales de la tarea
- Recomendaciones IA (visual)
- Asignación final con formulario

**6. Lista Técnicos**
- Buscador por nombre
- Filtros por zona y estado
- Tabla con avatares

**7. Detalle Técnico**
- Información del técnico
- Tareas asignadas hoy
- Estadísticas del mes

**8. Riesgos SLA**
- Lista de riesgos con filtros
- Detalle de riesgo con SLA

**9. Mapa de Tareas**
- Mapa de España con Leaflet
- Marcadores por tipo (incidencia/mantenimiento/puesta_marcha)
- Filtros por tipo, estado, técnico

**10. Asistente de Asignación** ✅ NUEVO
- Panel izquierdo: Carga de trabajo de cada técnico
- Panel derecho: Tareas pendientes por asignar
- Botón "Generar Recomendaciones" → Algoritmo VRP
- Click en tarea → Modal con explicación IA
- Botón "Editar" para cambiar técnico y prioridad
- Botón "Confirmar" para aplicar asignación
- Configuración de algoritmo (pesos ajustables)

---

## Tipos de Tareas (Colores)

| Tipo | Color | Descripción |
|------|-------|-------------|
| **Incidencia** | 🔴 Rojo | Problemas/averías |
| **Mantenimiento** | 🔵 Azul | Mantenimiento preventivo |
| **Puesta en Marcha** | 🟢 Verde | Nueva instalación |

---

## Estados de Tareas

| Estado | Descripción |
|--------|-------------|
| Por asignar | Sin técnico asignado |
| Asignada | En proceso (tiene técnico) |
| Resuelta | Completada |

---

## Rutas Implementadas

| Ruta | Blueprint | Descripción |
|------|-----------|-------------|
| `/login` | auth | Login |
| `/logout` | auth | Logout |
| `/dashboard` | main | Dashboard principal |
| `/panel` | main | Panel de control |
| `/tareas` | tareas | Lista de tareas |
| `/tareas/<id>` | tareas | Detalle de tarea |
| `/mapa` | mapa | Mapa de tareas |
| `/api/tareas-mapa` | mapa | API del mapa |
| `/asignacion` | asignacion | Asistente de asignación (NUEVO) |
| `/api/asignacion/datos` | asignacion | Datos de técnicos y tareas |
| `/api/asignacion/recomendar` | asignacion | Genera recomendaciones |
| `/api/asignacion/asignar` | asignacion | Confirma asignación |
| `/tecnicos` | tecnicos | Lista de técnicos |
| `/tecnicos/<id>` | tecnicos | Detalle de técnico |
| `/riesgos` | riesgos | Lista de riesgos SLA |
| `/riesgos/<id>` | riesgos | Detalle de riesgo |

---

## Servicios de IA

### VRP Optimizer (`services/vrp_optimizer.py`)
- Algoritmo de puntuación ponderada
- Factores: distancia (30%), carga trabajo (25%), zona (25%), SLA (20%)
- Función Haversine para calcular distancias

### IA Explicación (`services/ia_explicacion.py`)
- Genera explicaciones basadas en reglas
- Preparado para usar Groq/Llama (requiere API key)

---

## Archivos Nuevos

- `/apps/manager-web/src/routes/asignacion.py` - Ruta + API de asignación
- `/apps/manager-web/src/templates/asignacion.html` - UI del asistente
- `/apps/manager-web/src/services/vrp_optimizer.py` - Algoritmo VRP
- `/apps/manager-web/src/services/ia_explicacion.py` - Servicio de explicaciones

---

## Estado Actual (Marzo 2026)

### ✅ Completado
- App Flask funcionando en puerto 5000
- Login hardcodeado operativo
- Dashboard, Panel, Tareas, Técnicos, Riesgos
- Mapa de tareas con filtros
- Asistente de asignación con algoritmo VRP
- Modal de explicación + edición
- Navegación superior funcional
- **Integración con Firebase Firestore** ✅ NUEVO
- Datos importados desde JSON a Firestore

### ⏳ Pendiente
- IA real (Groq + Llama) para explicaciones
- Filtros JavaScript en listas
- App Flutter para técnicos
- Autoaprendizaje (guardar correcciones)

---

## Notas Importantes

1. Login actual es HARDCODED - sin base de datos (temporal)
2. La base de datos será Firebase Firestore
3. IA usará Groq con modelo Llama 3.1 (gratis, sin límites diarios)
4. Las tareas vendrán de Firebase
5. La IA debe explicar el "por qué" de sus recomendaciones
6. Debe tener autoaprendizaje (guardar correcciones del usuario)
7. Las tareas vendrán de un sistema externo ya creado
8. Operaciones solo asigna prioridad y técnico, no crea tareas

---

## Próximos Pasos Sugeridos

1. Conectar todos los módulos con Firebase
2. Configurar API de Groq para explicaciones más naturales
3. Implementar sistema de autoaprendizaje
4. Crear app Flutter para técnicos
5. Añadir más datos de ejemplo