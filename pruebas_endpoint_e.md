# Pruebas Endpoint E — Perfil Dual

## GET /analitica/perfil/{id}

### Escenario 1: Personaje no existe en ninguna BD
- **Request:** GET /analitica/perfil/personaje-inexistente
- **Expected:** 404 `{"detail": "Personaje 'personaje-inexistente' no encontrado en ninguna base de datos"}`

### Escenario 2: Personaje existe en ambas BD
- **Request:** GET /analitica/perfil/harry-potter
- **Expected:** 200 con `vista_mongo` y `vista_sql` completos, `warning: null`

### Escenario 3: Personaje solo en MongoDB
- **Request:** GET /analitica/perfil/{id-solo-en-mongo}
- **Expected:** 200 con `vista_mongo` completo, `vista_sql: null`, `warning: "Personaje existe en MongoDB pero no en MySQL"`

### Escenario 4: Personaje solo en MySQL
- **Request:** GET /analitica/perfil/{id-solo-en-sql}
- **Expected:** 200 con `vista_mongo: null`, `vista_sql` completo, `warning: "Personaje existe en MySQL pero no en MongoDB"`