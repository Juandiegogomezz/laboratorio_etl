-- =====================================================================
-- Validación del Endpoint D: GET /api/v1/analitica/columna/{nombre}
-- Responsable: Yohana
-- Uso: ejecutar en DBeaver y comparar con la respuesta del endpoint.
-- =====================================================================

USE etl_hp;

-- ---------------------------------------------------------------------
-- 0. Tipos de las columnas (base de la detección dinámica)
-- ---------------------------------------------------------------------
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'etl_hp' AND TABLE_NAME = 'personajes_hp'
ORDER BY ORDINAL_POSITION;

-- Total de registros (si da 0, el endpoint responde 404)
SELECT COUNT(*) AS total_registros FROM personajes_hp;


-- ---------------------------------------------------------------------
-- 1. Columna CATEGÓRICA (ejemplo: casa)
--    Compara con: distribucion, valor_mas_comun, sin_dato ("N/A") y nulos
-- ---------------------------------------------------------------------
SELECT casa, COUNT(*) AS cantidad
FROM personajes_hp
GROUP BY casa
ORDER BY cantidad DESC;

-- valores_unicos (sin contar "N/A")
SELECT COUNT(DISTINCT casa) AS valores_unicos
FROM personajes_hp
WHERE casa <> 'N/A';


-- ---------------------------------------------------------------------
-- 2. Columna de TEXTO LIBRE (ejemplo: nombre)
--    Compara con: valores_unicos y nulos
-- ---------------------------------------------------------------------
SELECT COUNT(DISTINCT nombre) AS valores_unicos,
       SUM(nombre IS NULL) AS nulos
FROM personajes_hp;

-- Por qué se usa un umbral del 90% y no "todos distintos":
-- hay personajes distintos (distinto id) con el mismo nombre
SELECT nombre, COUNT(*) AS veces
FROM personajes_hp
GROUP BY nombre
HAVING COUNT(*) > 1;


-- ---------------------------------------------------------------------
-- 3. Columna NUMÉRICA (ejemplo: total_trabajos)
--    Compara con: min, max, promedio, desviacion_std y nulos
--    Nota: Pandas calcula la desviación muestral (n - 1) = STDDEV_SAMP.
--    MySQL no tiene mediana; esa solo la calcula el endpoint con Pandas.
-- ---------------------------------------------------------------------
SELECT MIN(total_trabajos) AS minimo,
       MAX(total_trabajos) AS maximo,
       ROUND(AVG(total_trabajos), 2) AS promedio,
       ROUND(STDDEV_SAMP(total_trabajos), 2) AS desviacion,
       SUM(total_trabajos IS NULL) AS nulos
FROM personajes_hp;


-- ---------------------------------------------------------------------
-- 4. Columna de FECHA (ejemplo: fecha_nacimiento)
--    Compara con: min, max, rango_dias y nulos
-- ---------------------------------------------------------------------
SELECT MIN(fecha_nacimiento) AS minimo,
       MAX(fecha_nacimiento) AS maximo,
       DATEDIFF(MAX(fecha_nacimiento), MIN(fecha_nacimiento)) AS rango_dias,
       SUM(fecha_nacimiento IS NULL) AS nulos
FROM personajes_hp;

-- Fechas válidas (las que no se pudieron convertir quedaron en NULL)
SELECT nombre, fecha_nacimiento
FROM personajes_hp
WHERE fecha_nacimiento IS NOT NULL
ORDER BY fecha_nacimiento;


-- ---------------------------------------------------------------------
-- 5. Columna BOOLEANA (ejemplo: esta_vivo)
--    MySQL guarda BOOLEAN como TINYINT(1): 1 = true, 0 = false
--    Compara con: true, false y nulos
-- ---------------------------------------------------------------------
SELECT SUM(esta_vivo = 1) AS verdaderos,
       SUM(esta_vivo = 0) AS falsos,
       SUM(esta_vivo IS NULL) AS nulos
FROM personajes_hp;