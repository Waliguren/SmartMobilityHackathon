# Modelo de Datos

## Principio de diseño

El modelo separa claramente:

- inventario y contratos
- incidencias operativas
- visitas ejecutables
- planificación semanal y secuencia de ruta

## Entidades principales

### Client

- nombre
- peso o impacto de cliente
- prioridad comercial agregada

### Charger

- referencia externa
- ubicación geográfica
- zona operativa
- relación con cliente y contrato
- id opcional de OpenChargeMap

### Contract

- cliente
- cargador
- tipo de contrato
- `sla_priority` donde `0` es prioridad máxima
- tiempos objetivo de respuesta y resolución

### Incidence

- contrato y cargador afectados
- planificador que la abre
- nivel de urgencia
- impacto cliente
- fecha límite operativa
- posibilidad de autocrear visita

### Technician

- zona principal
- base geográfica
- disponibilidad semanal
- capacidad diaria de trabajo

### Visit

- correctiva o preventiva
- asociada a incidencia o contrato
- duración estimada
- deadline
- score heurístico calculado
- asignación a técnico y plan semanal

### RoutePlan

- técnico
- semana de planificación
- motor que generó el plan
- métricas agregadas de distancia y tiempo

### RouteStop

- secuencia dentro de un plan
- visita asociada
- llegada/salida previstas
- distancia y tiempo desde la parada anterior

### Report

- visita ejecutada
- resumen
- estado de cierre
- timestamps de creación y cierre

## Fuente de verdad

- PostgreSQL/PostGIS: fuente operacional principal
- Firebase: auth y almacenamiento de evidencias

## Índices previstos

- `charger.zone`
- `technician.zone`
- `incidence.status`
- `incidence.due_at`
- `visit.status`
- `visit.technician_id`
- `route_plan.week_start_date`

## Evolución prevista

En una siguiente iteración conviene añadir:

- calendario laboral del técnico
- skills o certificaciones por técnico
- reglas de compatibilidad por tipo de cargador
- eventos de replanificación intradía