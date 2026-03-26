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
| **Mapas** | Flutter Map / Google Maps API |

---

## Estructura del Proyecto

```
SmartMobilityHackathon/
├── apps/
│   ├── manager-web/        # App Flask - EN DESARROLLO
│   │   ├── src/
│   │   │   ├── routes/    # auth.py, main.py, tareas.py
│   │   │   ├── templates/ # HTML templates
│   │   │   ├── models/    # User model
│   │   │   └── static/    # CSS, JS
│   │   ├── config.py
│   │   ├── run.py
│   │   └── requirements.txt
│   └── technician-mobile/  # App Flutter - PENDIENTE
├── backend/                # Firebase Functions - PENDIENTE
├── docker-compose.yml
├── docs/
├── Material Suport Hackato SmAIrt Mobility/  # Material original
└── CONTEXTO_PROYECTO.md    # Este archivo
```

---

## Funcionalidades Acordadas

### App de Escritorio (Operaciones) - ACTUAL

**1. Login hardcodeado** (IMPLEMENTADO)
- Email: admin@smartmobility.com
- Password: admin123

**2. Dashboard** - Resumen de tareas, métricas (IMPLEMENTADO)
**3. Panel de Control** - Estadísticas, tareas críticas (IMPLEMENTADO)
**4. Gestión de Tareas** - Lista filtrable (IMPLEMENTADO)
**5. Detalle de Tarea** - Recomendaciones IA (visual, IMPLEMENTADO)

### IA de Recomendaciones - PENDIENTE

**Sistema de prioridades (algoritmo de puntuación):**
- Tipo incidencia (25%): Crítica=100, Alta=70, Media=40, Baja=20
- Tipo visita (20%): Correctivo=100, Preventivo=50, PuestaMarcha=30
- Urgencia SLA (30%): Según tiempo restante
- Tipo cliente (15%): Premium=100, Estándar=50, Básico=25
- Días sin atender (10%)

**Recomendación de técnico (algoritmo de matching):**
- Zona coincide (35%)
- Carga trabajo (25%)
- Distancia (20%)
- Disponibilidad (15%)
- Especialización (5%)

**Explicaciones**: La IA debe explicar "por qué" de sus recomendaciones

**Autoaprendizaje**: Guardar correcciones del usuario para ajustar pesos

### SLA Definidos

| Cliente | Respuesta | Resolución |
|---------|-----------|------------|
| Premium | 4h | 24h |
| Estándar | 8h | 48h |
| Básico | 24h | 72h |

Multiplicadores por tipo de incidencia:
- Crítica: x0.5
- Alta: x0.75
- Media: x1.0
- Baja: x1.5

### Flujo de Trabajo

1. **Departamento de Operaciones**: Asigna prioridad y técnico a tareas (con ayuda de IA)
2. **Técnicos**: Reciben tareas en su app móvil, planifican su ruta con sugerencias del algoritmo

---

## Estado Actual (Marzo 2026)

### ✅ Completado
- App Flask funcionando en puerto 5000
- Login hardcodeado operativo
- Dashboard accesible
- Panel de control implementado
- Lista de tareas implementada
- Detalle de tareas con UI de recomendaciones IA
- Base de datos SQLite local (no usada para login)

### ⏳ Pendiente
- Base de datos real (Firebase Firestore)
- IA real (Groq + Llama 3.1)
- Conexión con Firebase
- API endpoints para tareas
- App Flutter para técnicos

---

## Historial de Conversación

### 26 Marzo 2026 - Desarrollo Inicial
1. Revisado material de soporte del Hackathon
2. Definido Stack tecnológico (Flutter + Electron + Firebase + Groq)
3. Diseñada arquitectura de la app de escritorio
4. Implementado sistema de login con Flask
5. Creadas páginas: Dashboard, Panel, Tareas, Detalle
6. Configurada base de datos SQLite (no usada - hardcoded login)
7. Corregidos imports de módulos (app → src)
8. Guardado contexto inicial

---

## Archivos Creados

- `/apps/manager-web/src/__init__.py` - App factory Flask
- `/apps/manager-web/src/routes/auth.py` - Login/register/logout
- `/apps/manager-web/src/routes/main.py` - Dashboard/Panel
- `/apps/manager-web/src/routes/tareas.py` - Tareas
- `/apps/manager-web/src/models/user.py` - Modelo usuario
- `/apps/manager-web/src/templates/base.html` - Layout base
- `/apps/manager-web/src/templates/dashboard.html` - Dashboard
- `/apps/manager-web/src/templates/panel.html` - Panel control
- `/apps/manager-web/src/templates/auth/login.html` - Login
- `/apps/manager-web/src/templates/auth/register.html` - Registro
- `/apps/manager-web/src/templates/tareas/lista.html` - Lista tareas
- `/apps/manager-web/src/templates/tareas/detalle.html` - Detalle tarea
- `/apps/manager-web/src/static/css/style.css` - Estilos Bootstrap
- `/apps/manager-web/src/static/js/main.js` - JS
- `/apps/manager-web/config.py` - Configuración
- `/apps/manager-web/run.py` - Punto de entrada
- `/apps/manager-web/requirements.txt` - Dependencias

---

## Notas Importantes

1. Login actual es HARDCODED - sin base de datos (temporal)
2. La base de datos será Firebase Firestore (no SQLite)
3. IA usará Groq con modelo Llama 3.1 (gratis, sin límites diarios)
4. Las tareas vendrán de Firebase (no se crean manualmente en la app)
5. La IA debe explicar el "por qué" de sus recomendaciones
6. Debe tener autoaprendizaje (guardar correcciones del usuario)
7. Las tareas vendrán de un sistema externo ya creado
8. Operaciones solo asigna prioridad y técnico, no crea tareas

---

## Próximos Pasos Sugeridos

1. Configurar proyecto Firebase y credenciales
2. Crear estructura de datos en Firestore
3. Implementar API de tareas conectando a Firebase
4. Implementar servicio Groq para recomendaciones de prioridad
5. Implementar servicio Groq para recomendaciones de técnico
6. Añadir sistema de autoaprendizaje
7. Mejorar UI del detalle de tareas
8. Crear app Flutter para técnicos