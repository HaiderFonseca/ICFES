-- Eliminar la vista materializada si ya existe
DROP MATERIALIZED VIEW IF EXISTS puntajes_promedio_por_naturaleza;

-- Crear la vista materializada para calcular el puntaje promedio por colegio_naturaleza
CREATE MATERIALIZED VIEW puntajes_promedio_por_naturaleza AS
SELECT
    colegio_naturaleza,
    AVG(puntaje_ingles) AS promedio_puntaje_ingles,
    AVG(puntaje_matematicas) AS promedio_puntaje_matematicas,
    AVG(puntaje_sociales_ciudadanas) AS promedio_puntaje_sociales_ciudadanas,
    AVG(puntaje_ciencias_naturales) AS promedio_puntaje_ciencias_naturales,
    AVG(puntaje_lectura_critica) AS promedio_puntaje_lectura_critica,
    AVG(puntaje_global) AS promedio_puntaje_global
FROM datos
GROUP BY colegio_naturaleza;

-- Crear un índice para mejorar el rendimiento de las consultas
CREATE INDEX idx_puntajes_promedio_por_naturaleza ON puntajes_promedio_por_naturaleza (colegio_naturaleza);
