# laboratorio_etl
desarrollo de api con todos los personajes de harry potter

## Daniela Salazar — Transformación y carga
- Modelo `Personaje` (tabla `personajes_hp`, 12 columnas, PK = `_id` de Mongo).
- Endpoint `POST /api/v1/etl/transformar`: limpieza con Pandas y upsert en MySQL.
- Consultas de validación en `consultas_validacion.sql`.


## Juan Silva — Endpoint E: Perfil Dual

- Schema `PerfilDualResponse` en `app/views/schemas.py`.
- Consulta MongoDB por `_id` y MySQL por `id_personaje`.
- Endpoint `GET /api/v1/analitica/perfil/{id}`: retorna vista dual con 4 escenarios posibles (ambas BD, solo Mongo, solo MySQL, 404).
- Controller en `app/controllers/perfil_dual_controller.py`.
- Service en `app/services/perfil_dual_service.py`.