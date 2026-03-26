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
│   │   │   ├── routes/     # auth.py, main.py, tareas.py, tecnicos.py, riesgos.py, mapa.py
│   │   │   ├── templates/  # HTML templates
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
- Enlaces funcionales a: /riesgos, /tecnicos

**3. Panel de Control**
- Estadísticas con iconos (todos clickeables)
- Tareas críticas listadas
- Técnicos por zona (gráficos de progreso)

**4. Gestión de Tareas**
- Lista con filtros (Tipo, Zona, Prioridad)
- Tabs: Pendientes, Asignadas, Completadas
- Paginación

**5. Detalle de Tarea**
- Datos generales de la tarea
- Recomendaciones IA (visual)
- Asignación final con formulario

**6. Lista Técnicos**
- Buscador por nombre
- Filtros por zona y estado
- Tabla con: ID, Nombre, Zona, Tareas Hoy, Estado
- Avatares con iniciales

**7. Detalle Técnico**
- Información del técnico
- Tareas asignadas hoy
- Estadísticas del mes

**8. Lista Riesgos SLA**
- Alerta de riesgos críticos
- Lista de tareas en riesgo
- Filtros por severidad

**9. Detalle Riesgo**
- Información del riesgo
- SLA detallado (respuesta y resolución)
- Acciones rápidas

**10. Mapa de Tareas** ✅ NUEVO
- Mapa de España con Leaflet + OpenStreetMap
- Marcadores circulares por tipo:
  - 🔴 Incidencia (rojo)
  - 🔵 Mantenimiento (azul)
  - 🟢 Puesta en Marcha (verde)
- Filtros por tipo, estado y técnico
- Estadísticas en tiempo real
- Popup con detalles al hacer click
- Leyenda visible

---

## Tipos de Tareas (Colores)

| Tipo | Color | Descripción |
|------|-------|-------------|
| **Incidencia** | 🔴 Rojo | Problemas/averías |
| **Mantenimiento** | 🔵 Azul | Mantenimiento preventivo |
| **Puesta en Marcha** | 🟢 Verde | Nueva instalación |

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
| `/mapa` | mapa | Mapa de tareas (NUEVO) |
| `/api/tareas-mapa` | mapa | API de tareas para el mapa |
| `/tecnicos` | tecnicos | Lista de técnicos |
| `/tecnicos/<id>` | tecnicos | Detalle de técnico |
| `/riesgos` | riesgos | Lista de riesgos SLA |
| `/riesgos/<id>` | riesgos | Detalle de riesgo |

---

## Archivos Creados/Actualizados

- `/apps/manager-web/src/routes/mapa.py` - NUEVO: Ruta del mapa + API
- `/apps/manager-web/src/templates/mapa.html` - NUEVO: Página con Leaflet
- `/apps/manager-web/src/__init__.py` - Actualizado con blueprint mapa
- `/apps/manager-web/src/templates/base.html` - Actualizado con navegación

---

## Estado Actual (Marzo 2026)

### ✅ Completado
- App Flask funcionando en puerto 5000
- Login hardcodeado operativo
- Dashboard con enlaces funcionales
- Panel de control con elementos clickeables
- Lista de tareas implementada
- Detalle de tareas con UI de recomendaciones IA
- Lista de técnicos implementada
- Detalle de técnico implementado
- Lista de riesgos SLA implementada
- Detalle de riesgos implementado
- Mapa de tareas con filtros por tipo, estado y técnico
- Navegación superior funcional

### ⏳ Pendiente
- Filtros con JavaScript en listas
- Base de datos real (Firebase Firestore)
- IA real (Groq + Llama)
- Conexión con Firebase
- App Flutter para técnicos

---

## Notas Importantes

1. Login actual es HARDCODED - sin base de datos (temporal)
2. La base de datos será Firebase Firestore (no SQLite)
3. IA usará Groq con modelo Llama 3.1 (gratis, sin límites diarios)
4. Las tareas vendrán de Firebase
5. La IA debe explicar el "por qué" de sus recomendaciones
6. Debe tener autoaprendizaje (guardar correcciones del usuario)
7. Las tareas vendrán de un sistema externo ya creado
8. Operaciones solo asigna prioridad y técnico, no crea tareas

---

## Próximos Pasos Sugeridos

1. Conectar mapa con Firebase para datos reales
2. Implementar filtros con JavaScript en listas
3. Configurar proyecto Firebase y credenciales
4. Crear estructura de datos en Firestore
5. Implementar servicio Groq para recomendaciones
6. Crear app Flutter para técnicos