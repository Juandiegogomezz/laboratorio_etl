# laboratorio_etl
desarrollo de api con todos los personajes de harry potter

## Endpoint D: Análisis por columna (Yohana)

`GET /api/v1/analitica/columna/{nombre}`

Recibe el nombre de una columna de la tabla `personajes_hp` y devuelve un análisis estadístico según su tipo. El tipo se detecta de forma dinámica a partir del modelo SQLAlchemy (`Personaje.__table__.columns`), sin usar nombres de columna fijos.

| Tipo SQL de la columna | Tipo detectado | Qué devuelve |
|---|---|---|
| `Boolean` | booleana | `true`, `false`, `nulos` |
| `Date` / `DateTime` | fecha | `min`, `max`, `rango_dias`, `nulos` |
| `Integer` / `Float` / `Numeric` | numerica | `min`, `max`, `promedio`, `mediana`, `desviacion_std`, `nulos` |
| Texto con 90% o más de valores distintos | texto | `valores_unicos`, `nulos` |
| Texto con valores repetidos | categorica | `valores_unicos`, `distribucion`, `valor_mas_comun`, `sin_dato` ("N/A"), `nulos` |

Respuestas de error:
- **400**: la columna no existe; incluye la lista de columnas válidas.
- **404**: la tabla está vacía; hay que ejecutar primero `/etl/transformar`.
- **500**: error inesperado al leer o analizar la columna.

Archivos:
- `app/controllers/analitica_controller.py`: ruta y manejo de errores HTTP.
- `app/services/analitica_service.py`: lectura con Pandas, detección del tipo y análisis.
- `app/views/schemas.py`: schemas de respuesta del análisis.
- `validacion_analitica_columna.sql`: consultas para validar los resultados en DBeaver.
- `postman/Endpoint_D_analisis_columna.postman_collection.json`: colección de Postman con una prueba por tipo y el caso 400.
