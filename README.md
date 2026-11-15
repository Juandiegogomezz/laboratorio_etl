# laboratorio_etl
desarrollo de api con todos los personajes de harry potter

## Daniela Salazar — Transformación y carga
- Modelo `Personaje` (tabla `personajes_hp`, 12 columnas, PK = `_id` de Mongo).
- Endpoint `POST /api/v1/etl/transformar`: limpieza con Pandas y upsert en MySQL.
- Consultas de validación en `consultas_validacion.sql`.