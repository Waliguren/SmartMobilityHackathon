# Desarrollo

## Convenciones iniciales

- TypeScript para frontend web
- Dart para móvil
- Python 3.12 para backend
- Documentación en Markdown dentro de `docs/`

## Estrategia de ramas

- `main`: base estable del hackathon
- ramas cortas por feature o spike

## Siguientes pasos sugeridos

1. Definir los flujos exactos del PDF en historias de usuario.
2. Cerrar el modelo de datos de Firestore a partir del ERD actual.
3. Acordar diseño de autenticación y roles.
4. Implementar primero contratos, incidencias y visitas en backend.
5. Construir después las vistas de gestión y la agenda móvil.

## Criterios para la siguiente iteración

- Endpoints base versionados en `/api/v1`
- Tipado compartido de entidades entre frontend y backend
- Estados de dominio definidos de forma explícita
- Seed mínimo de datos para desarrollo