-- Consultas de validación para DBeaver (tabla personajes_hp)

-- 1. Estructura: tipos de cada columna y PK
DESCRIBE personajes_hp;
SHOW KEYS FROM personajes_hp WHERE Key_name = 'PRIMARY';

-- 2. Total de registros (debe coincidir con "registros_procesados" de /transformar)
SELECT COUNT(*) AS total_registros FROM personajes_hp;

-- 3. Idempotencia: no debe haber PK repetidas (debe devolver 0 filas)
SELECT id_personaje, COUNT(*) AS veces
FROM personajes_hp
GROUP BY id_personaje
HAVING COUNT(*) > 1;

-- 4. Nulos y "N/A" por columna
SELECT
    SUM(fecha_nacimiento IS NULL) AS fecha_nacimiento_nulos,
    SUM(total_trabajos IS NULL)   AS total_trabajos_nulos,
    SUM(esta_vivo IS NULL)        AS esta_vivo_nulos,
    SUM(especie = 'N/A')          AS especie_na,
    SUM(genero = 'N/A')           AS genero_na,
    SUM(casa = 'N/A')             AS casa_na,
    SUM(estatus_sangre = 'N/A')   AS estatus_sangre_na,
    SUM(nacionalidad = 'N/A')     AS nacionalidad_na,
    SUM(estado_civil = 'N/A')     AS estado_civil_na,
    SUM(patronus = 'N/A')         AS patronus_na
FROM personajes_hp;

-- 5. Columna categórica (comparar con /analitica/columna/casa)
SELECT casa, COUNT(*) AS cantidad
FROM personajes_hp
GROUP BY casa
ORDER BY cantidad DESC;

-- 6. Columna numérica (comparar con /analitica/columna/total_trabajos)
SELECT
    MIN(total_trabajos) AS min,
    MAX(total_trabajos) AS max,
    ROUND(AVG(total_trabajos), 2) AS promedio,
    ROUND(STDDEV_SAMP(total_trabajos), 2) AS desviacion_std
FROM personajes_hp;

-- 7. Columna fecha (comparar con /analitica/columna/fecha_nacimiento)
SELECT
    MIN(fecha_nacimiento) AS min,
    MAX(fecha_nacimiento) AS max,
    DATEDIFF(MAX(fecha_nacimiento), MIN(fecha_nacimiento)) AS rango_dias,
    SUM(fecha_nacimiento IS NULL) AS nulos
FROM personajes_hp;

-- 8. Columna booleana (comparar con /analitica/columna/esta_vivo)
SELECT esta_vivo, COUNT(*) AS cantidad
FROM personajes_hp
GROUP BY esta_vivo;

-- 9. Validación cruzada (comparar con Mongo Compass y /analitica/perfil/harry-potter)
SELECT * FROM personajes_hp WHERE id_personaje = 'harry-potter';