# laboratorio_etl

Desarrollo de una API con todos los personajes de Harry Potter: un pipeline ETL completo con **FastAPI** que extrae datos de la Hogwarts API, los guarda crudos en **MongoDB**, los limpia con **Pandas** y los carga en **MySQL**, y expone endpoints de analítica sobre los datos cargados.

---

## División de responsabilidades

| Integrante | Responsabilidad | Endpoint(s) |
|---|---|---|
| **Juan Diego** | Estructura base del proyecto (MVC + Services), `config.py`, `database.py` y `main.py`. Extracción y Reset. | `POST /api/v1/etl/extraer` · `DELETE /api/v1/etl/reset` |
| **Daniela Salazar** | Modelo `Personaje` (tabla `personajes_hp`) y Transformación y carga. | `POST /api/v1/etl/transformar` |
| **Yohana** | Analítica por columna con detección dinámica de tipos. | `GET /api/v1/analitica/columna/{nombre}` |
| **Juan Silva** | Perfil dual Mongo + SQL. | `GET /api/v1/analitica/perfil/{id}` |

### Detalle por integrante

**Juan Diego, Extracción y Reset**
- Estructura base del proyecto (MVC + Services), `config.py`, `database.py` y `main.py`.
- `POST /api/v1/etl/extraer`: consume la Hogwarts API por páginas y guarda en MongoDB con el `id` original como `_id` (upsert, idempotente).
- `DELETE /api/v1/etl/reset`: limpia MongoDB (`delete_many`) y MySQL (`TRUNCATE`).

**Daniela Salazar, Transformación y carga**
- Modelo `Personaje` (tabla `personajes_hp`, 12 columnas, PK = `_id` de Mongo).
- `POST /api/v1/etl/transformar`: limpieza con Pandas y upsert en MySQL.
- Consultas de validación en `consultas_validacion.sql`.

**Yohana, Endpoint D: Análisis por columna**
- `GET /api/v1/analitica/columna/{nombre}`: el tipo de la columna se detecta de forma dinámica a partir del modelo SQLAlchemy, sin nombres de columna fijos.
- Archivos: `app/controllers/analitica_controller.py`, `app/services/analitica_service.py`, `app/views/schemas.py`.
- `validacion_analitica_columna.sql`: consultas para validar los resultados en DBeaver.
- `postman/Endpoint_D_analisis_columna.postman_collection.json`: colección de Postman con una prueba por tipo y el caso 400.

**Juan Silva, Endpoint E: Perfil dual**
- Schema `PerfilDualResponse` en `app/views/schemas.py`.
- Consulta MongoDB por `_id` y MySQL por `id_personaje`.
- `GET /api/v1/analitica/perfil/{id}`: vista dual con 4 escenarios posibles (ambas BD, solo Mongo, solo MySQL, 404).
- Ruta en `app/controllers/analitica_controller.py` y lógica en `app/services/perfil_dual_service.py`.

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| FastAPI + Uvicorn | API REST |
| Pydantic | Validación de entradas y salidas (views) |
| Requests | Consumo de la Hogwarts API |
| MongoDB + PyMongo | Staging: datos crudos |
| Pandas + NumPy | Limpieza y transformación |
| MySQL + SQLAlchemy + mysql-connector-python | Data warehouse |
| python-dotenv | Variables de entorno |

---

## Arquitectura

### Flujo de datos

```
Hogwarts API (JSON)  ──►  MongoDB (staging, data cruda)  ──►  MySQL (data warehouse, tabla plana)
      extraer                      transformar (limpieza con Pandas + carga)
```

### Estructura de carpetas

```
laboratorio_etl/
├── .env                          # Credenciales (NO se sube al repo)
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
├── consultas_validacion.sql      # Consultas de validación de la tabla (DBeaver)
├── validacion_analitica_columna.sql  # Validación SQL del endpoint por columna
├── postman/
│   └── Endpoint_D_analisis_columna.postman_collection.json
└── app/
    ├── main.py                   # Inicializa FastAPI, crea la tabla e incluye los routers
    ├── config.py                 # Lee las variables del .env y arma la URL de MySQL
    ├── database.py               # Conexiones a MySQL (SQLAlchemy) y a MongoDB (PyMongo)
    ├── controllers/
    │   ├── etl_controller.py         # Rutas del pipeline: extraer, transformar, reset
    │   └── analitica_controller.py   # Rutas de analítica: columna y perfil
    ├── models/
    │   └── entidad_sql.py        # Modelo SQLAlchemy de la tabla personajes_hp
    ├── services/
    │   ├── etl_service.py            # Lógica del ETL (requests, Pandas, upsert, truncate)
    │   ├── analitica_service.py      # Lógica del análisis por columna
    │   └── perfil_dual_service.py    # Lógica del perfil dual Mongo + SQL
    └── views/
        └── schemas.py            # Esquemas Pydantic de entrada y salida
```

### Responsabilidad de cada capa (MVC + Services)

- **Controllers:** reciben la petición HTTP, validan con los esquemas de `views` y llaman al service. Traducen las excepciones a códigos HTTP.
- **Services:** contienen la lógica real (peticiones a la API, Pandas, consultas). No conocen HTTP.
- **Models:** definen la tabla SQL con SQLAlchemy.
- **Views:** esquemas Pydantic que validan los JSON de entrada y salida.

ETL y Analítica están separados en controllers y services distintos, de modo que cada uno puede cambiar sin afectar al otro.

---

## Instalación y configuración

### Requisitos previos

- Python 3.10 o superior
- MySQL en ejecución
- MongoDB en ejecución
- (Opcional) DBeaver, MongoDB Compass y Postman para inspeccionar y probar

### Pasos

1. **Clonar el repositorio y entrar a la carpeta**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd laboratorio_etl
   ```

2. **Crear y activar el entorno virtual**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac / Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Crear la base de datos en MySQL** (una sola vez, por ejemplo desde DBeaver). La tabla la crea la aplicación sola, pero la base debe existir:
   ```sql
   CREATE DATABASE etl_hp;
   ```

5. **Configurar el `.env`** copiando la plantilla:
   ```bash
   # Windows
   copy .env.example .env
   # Mac / Linux
   cp .env.example .env
   ```
   Y ajustar los valores:

   | Variable | Descripción | Valor de ejemplo |
   |---|---|---|
   | `MONGO_URI` | Cadena de conexión a MongoDB | `mongodb://localhost:27017` |
   | `MONGO_DB` | Base de datos en Mongo | `etl_hp` |
   | `MONGO_COLLECTION` | Colección con los datos crudos | `personajes_raw` |
   | `MYSQL_USER` | Usuario de MySQL | `root` |
   | `MYSQL_PASSWORD` | Contraseña de MySQL | (la de cada equipo) |
   | `MYSQL_HOST` | Host de MySQL | `localhost` |
   | `MYSQL_PORT` | Puerto de MySQL | `3306` |
   | `MYSQL_DB` | Base de datos en MySQL | `etl_hp` |
   | `API_URL` | Endpoint de personajes de la fuente | `https://hogwarts-api.com/api/characters` |

6. **Levantar la aplicación** desde la raíz del proyecto:
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Abrir la documentación interactiva (Swagger):** <http://127.0.0.1:8000/docs>

---

## Cómo funciona el pipeline

### 1. Extracción (E)

`etl_service.extraer(cantidad)`

- Pide a la API los personajes por páginas (`page`, `page_size=50`) hasta reunir la cantidad solicitada o hasta que no haya más páginas.
- A cada personaje se le asigna `_id = id`, de modo que la clave de Mongo es el **identificador original de la API** (un slug como `abraham-ronen`), no un `ObjectId` generado por Mongo.
- Guarda con `replace_one(..., upsert=True)`. Si el documento ya existía lo cuenta como `ya_existentes`; si no, como `nuevos`. Por eso, ejecutar el endpoint varias veces con la misma cantidad **no duplica datos** y en la segunda ejecución `nuevos` es 0.

### 2. Transformación (T)

`etl_service.limpiar_datos(documentos)`

| Paso | Qué hace |
|---|---|
| Campos faltantes | Si un campo no viene en ningún documento, se crea vacío para no romper el pipeline. |
| Vacíos de la API | Los textos vacíos `""` se convierten en nulos. |
| Aplanamiento y derivadas | `total_trabajos` = cantidad de elementos de la lista `jobs`. `esta_vivo` = `True` cuando `died` viene vacío. |
| Selección y renombrado | Se conservan solo las columnas necesarias, con nombres claros en español (mapeo `MAPEO_COLUMNAS`). |
| Descartes | Se eliminan registros sin `id` o sin `nombre`, y duplicados dentro del mismo lote. |
| Texto | Se quitan espacios; en columnas categóricas los vacíos pasan a `"N/A"`; el género se unifica con `title()` (`male`/`Male` → `Male`). |
| Fecha de nacimiento | La API trae texto libre (por ejemplo `"Between 1 September 1883 and 31 August 1884"`). Con una expresión regular se extrae la primera fecha **completa** (día, mes y año) y se convierte a `DATE`. Si no hay fecha completa (por ejemplo `"Before 1953"`), queda `NULL`. |
| Nulos finales | Todo `NaN`/`NaT` restante se convierte en `None`, es decir `NULL` en MySQL. |

**Criterio de nulos:** las columnas de texto categórico se rellenan con `"N/A"`, mientras que las numéricas y de fecha se dejan en `NULL`. Rellenar con 0 distorsionaría el promedio y la mediana, y `"N/A"` no es una fecha válida.

### 3. Carga (L)

`etl_service.transformar()`

- Lee **todos** los documentos de Mongo, los limpia y crea la tabla con `Base.metadata.create_all` si no existe (esto conserva la Primary Key).
- Inserta por lotes de 500 con `INSERT ... ON DUPLICATE KEY UPDATE`: si el `id_personaje` ya existe se actualiza la fila, si no se inserta. Por eso ejecutar el endpoint varias veces **no duplica filas**.
- La PK de MySQL (`id_personaje`) es exactamente el mismo valor que el `_id` de Mongo. Eso es lo que permite cruzar ambos registros en el Perfil Dual.

### 4. Reset

`etl_service.reset()`

- Borra todos los documentos de la colección de Mongo (`delete_many`).
- Cuenta las filas de MySQL y ejecuta `TRUNCATE TABLE`. **No** se usa `DROP`: la tabla queda existente y lista para la siguiente ejecución del pipeline.

---

## Endpoints

Prefijo común: `http://127.0.0.1:8000`

### A. Extracción

`POST /api/v1/etl/extraer`

Request body:
```json
{ "cantidad": 50 }
```

| Campo de respuesta | Descripción |
|---|---|
| `mensaje` | Mensaje de confirmación |
| `nuevos` | Documentos insertados por primera vez |
| `ya_existentes` | Documentos que ya estaban en Mongo (se reemplazan, no se duplican) |
| `fuente` | Nombre de la API de origen |
| `status` | `201` |

Errores: `422` si `cantidad` no es mayor que 0 (validación de Pydantic); `500` si falla la API externa o Mongo.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/etl/extraer \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 50}'
```

### B. Transformación y carga

`POST /api/v1/etl/transformar` (sin cuerpo)

| Campo de respuesta | Descripción |
|---|---|
| `mensaje` | Mensaje de confirmación |
| `registros_procesados` | Registros que quedaron tras la limpieza y se cargaron a MySQL |
| `tabla_destino` | `personajes_hp` |
| `status` | `200` |

Errores: `404` si Mongo está vacío (hay que ejecutar primero `/extraer`); `503` si no se puede leer Mongo; `500` si falla la carga en MySQL.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/etl/transformar
```

### C. Reset

`DELETE /api/v1/etl/reset`

| Campo de respuesta | Descripción |
|---|---|
| `mensaje` | Mensaje de confirmación |
| `mongo_docs_eliminados` | Documentos borrados de Mongo |
| `mysql_rows_eliminadas` | Filas que tenía la tabla antes del `TRUNCATE` |
| `status` | `200` |

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/etl/reset
```

### D. Análisis por columna

`GET /api/v1/analitica/columna/{nombre}`

Recibe el nombre de una columna de la tabla `personajes_hp` y devuelve un análisis estadístico según su tipo. El tipo se detecta de forma dinámica a partir del modelo SQLAlchemy (`Personaje.__table__.columns`), sin usar nombres de columna fijos: si el modelo cambia, el análisis se adapta solo.

| Tipo SQL de la columna | Tipo detectado | Qué devuelve |
|---|---|---|
| `Boolean` | booleana | `true`, `false`, `nulos` |
| `Date` / `DateTime` | fecha | `min`, `max`, `rango_dias`, `nulos` |
| `Integer` / `Float` / `Numeric` | numerica | `min`, `max`, `promedio`, `mediana`, `desviacion_std`, `nulos` |
| Texto con 90% o más de valores distintos | texto | `valores_unicos`, `nulos` |
| Texto con valores repetidos | categorica | `valores_unicos`, `distribucion`, `valor_mas_comun`, `sin_dato` (`"N/A"`), `nulos` |

Notas:
- En las categóricas, los `"N/A"` **no** se cuentan en la distribución: se reportan aparte como `sin_dato`.
- Las estadísticas numéricas se calculan solo sobre valores no nulos.

Respuestas de error:
- **400:** la columna no existe; incluye `columnas_validas`.
- **404:** la tabla está vacía; hay que ejecutar primero `/etl/transformar`.
- **500:** error inesperado al leer o analizar la columna.

```bash
curl http://127.0.0.1:8000/api/v1/analitica/columna/casa
curl http://127.0.0.1:8000/api/v1/analitica/columna/total_trabajos
curl http://127.0.0.1:8000/api/v1/analitica/columna/fecha_nacimiento
curl http://127.0.0.1:8000/api/v1/analitica/columna/esta_vivo
```

### E. Perfil dual (Mongo + SQL)

`GET /api/v1/analitica/perfil/{id}`

Devuelve el mismo registro visto desde las dos bases de datos. Sirve como auditoría del pipeline y demuestra que las PKs están alineadas. Consulta Mongo por `_id` y MySQL por `id_personaje`.

| Escenario | Respuesta |
|---|---|
| Existe en ambas bases | `200` con `vista_mongo` y `vista_sql` |
| Existe solo en una | `200` con la vista existente, la otra en `null` y un `warning` que explica la inconsistencia |
| No existe en ninguna | `404` |

Campos de la respuesta: `id`, `vista_mongo`, `vista_sql`, `warning`. El `id` se normaliza (sin espacios y en minúsculas) antes de consultar.

```bash
curl http://127.0.0.1:8000/api/v1/analitica/perfil/abraham-ronen
```

---

## Modelo de datos

Tabla `personajes_hp` (tabla plana, una sola entidad):

| Columna SQL | Tipo | Campo de la API | Limpieza |
|---|---|---|---|
| `id_personaje` | `VARCHAR(150)` **PK** (no autoincremental) | `id` (= `_id` en Mongo) | Obligatorio |
| `nombre` | `VARCHAR(150)` NOT NULL | `name` | `strip` |
| `especie` | `VARCHAR(50)` NOT NULL | `species` | vacío → `"N/A"` |
| `genero` | `VARCHAR(20)` NOT NULL | `gender` | vacío → `"N/A"`, unificado con `title()` |
| `casa` | `VARCHAR(30)` NOT NULL | `house` | vacío → `"N/A"` |
| `estatus_sangre` | `VARCHAR(50)` NOT NULL | `blood_status` | vacío → `"N/A"` |
| `nacionalidad` | `VARCHAR(50)` NOT NULL | `nationality` | vacío → `"N/A"` |
| `estado_civil` | `VARCHAR(50)` NOT NULL | `marital_status` | vacío → `"N/A"` |
| `patronus` | `VARCHAR(100)` NOT NULL | `patronus` | vacío → `"N/A"` |
| `fecha_nacimiento` | `DATE` NULL | `born` | Se extrae la primera fecha completa; si no hay, `NULL` |
| `total_trabajos` | `INT` NULL | `jobs` (derivada) | Cantidad de elementos de la lista |
| `esta_vivo` | `BOOLEAN` NULL | `died` (derivada) | `True` si `died` viene vacío |

---

## Guía de uso (flujo recomendado)

1. **Reset:** `DELETE /api/v1/etl/reset` para partir de un estado limpio.
2. **Extraer:** `POST /api/v1/etl/extraer` con la cantidad deseada.
3. **Transformar:** `POST /api/v1/etl/transformar`.
4. **Analítica:** `GET /api/v1/analitica/columna/{nombre}` con distintas columnas.
5. **Perfil dual:** `GET /api/v1/analitica/perfil/{id}` con un `_id` real.

### Comprobar la idempotencia

- Ejecuta `/extraer` dos veces con la misma cantidad: en la segunda, `nuevos` debe ser `0` y `ya_existentes` igual a la cantidad.
- Ejecuta `/transformar` dos veces: el `COUNT(*)` de `personajes_hp` no debe cambiar.
- Verifica en Compass que el número de documentos no crece, y en DBeaver que la tabla no tiene PKs repetidas.

---

## Validación y pruebas

- **Postman:** `postman/Endpoint_D_analisis_columna.postman_collection.json` incluye una prueba por tipo de columna y el caso 400. Se importa desde **Import** en Postman.
- **SQL de validación de la tabla:** `consultas_validacion.sql` (conteos, nulos, tipos de datos y PK).
- **SQL de validación de la analítica:** `validacion_analitica_columna.sql` contiene las consultas equivalentes a lo que devuelve el endpoint por columna, para compararlas en DBeaver.
- **Documentación interactiva:** `/docs` (Swagger) permite probar cada endpoint desde el navegador.

---

## Decisiones de diseño

- **PK natural:** se usa el `id` de la API (un slug de texto) como `_id` en Mongo y como PK en MySQL, sin autoincrementales. Así el mismo registro tiene el mismo identificador en ambas bases.
- **Upsert en lugar de verificar e insertar:** `replace_one(upsert=True)` en Mongo y `ON DUPLICATE KEY UPDATE` en MySQL hacen la operación atómica y garantizan la idempotencia.
- **No se usa `df.to_sql(if_exists="replace")`:** borraría la tabla y su PK, rompiendo la idempotencia, el `TRUNCATE` y el perfil dual. La tabla se crea desde el modelo con `Base.metadata.create_all`.
- **`TRUNCATE` y no `DROP`:** el reset deja la estructura intacta y lista para reutilizarse.
- **Nulos según el tipo de dato:** `"N/A"` en texto categórico; `NULL` en fechas y numéricos para no sesgar las estadísticas ni inventar fechas inválidas.
- **Detección dinámica de tipos:** la analítica lee los tipos del modelo SQLAlchemy, por lo que se adapta a cualquier tabla sin nombres de columna fijos.
- **Textos libres vs. categóricos:** para columnas de texto se usa un umbral del 90% de valores distintos (`UMBRAL_TEXTO_LIBRE`) para decidir si es texto libre o categoría.
- **Separación ETL / Analítica:** controllers y services independientes para cada responsabilidad.
- Schema `PerfilDualResponse` en `app/views/schemas.py`.
- Consulta MongoDB por `_id` y MySQL por `id_personaje`.
- Endpoint `GET /api/v1/analitica/perfil/{id}`: retorna vista dual con 4 escenarios posibles (ambas BD, solo Mongo, solo MySQL, 404).
- Ruta en `app/controllers/analitica_controller.py`.
- Service en `app/services/perfil_dual_service.py`.
