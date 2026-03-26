# Motor de Planificación

## Objetivo

Asignar visitas semanales a técnicos de forma operativa, priorizando correctamente y reduciendo desplazamientos.

## Entradas principales

- incidencias abiertas
- visitas pendientes
- contratos y prioridad SLA
- impacto cliente
- urgencia
- zona y base de cada técnico
- deadlines operativos

## Heurística base

Cada visita recibe un `heuristic_score` calculado con una combinación ponderada de:

- prioridad SLA
- urgencia
- impacto cliente
- cercanía del deadline

## Distancias y routing

La estrategia prevista es de varias capas:

1. `Google Fleet Routing` si hay credenciales y se decide usarlo.
2. `A*` sobre un grafo viario cargado desde GeoJSON si hay dataset local.
3. `Haversine` como fallback operativo cuando no haya grafo disponible.

## Restricciones iniciales

- no asignar tareas fuera de una distancia razonable del técnico salvo necesidad explícita
- respetar capacidad diaria estimada
- favorecer que una tarea crítica se coloque antes en la semana
- permitir libertad de ejecución dentro de la semana, pero con deadlines estrictos para tareas críticas

## Resultado esperado

- plan semanal por técnico
- orden de paradas
- estimación de km y minutos de desplazamiento
- lista de visitas no asignadas si no hay capacidad suficiente

## Limitaciones de esta iteración

- no hay todavía optimización exacta tipo VRP completa
- la secuenciación inicial es heurística
- la calidad final dependerá del grafo viario disponible y de los pesos de scoring