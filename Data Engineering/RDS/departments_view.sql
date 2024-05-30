-- Eliminar la vista materializada si ya existe
DROP MATERIALIZED VIEW IF EXISTS puntajes_promedio_por_departamento;

-- Crear la vista materializada para calcular el puntaje promedio por departamento
CREATE MATERIALIZED VIEW puntajes_promedio_por_departamento AS
SELECT
    colegio_departamento,
    AVG(puntaje_ingles) AS promedio_puntaje_ingles,
    AVG(puntaje_matematicas) AS promedio_puntaje_matematicas,
    AVG(puntaje_sociales_ciudadanas) AS promedio_puntaje_sociales_ciudadanas,
    AVG(puntaje_ciencias_naturales) AS promedio_puntaje_ciencias_naturales,
    AVG(puntaje_lectura_critica) AS promedio_puntaje_lectura_critica,
    AVG(puntaje_global) AS promedio_puntaje_global
FROM datos
GROUP BY colegio_departamento;

-- Crear un índice para mejorar el rendimiento de las consultas
CREATE INDEX idx_puntajes_promedio_por_departamento ON puntajes_promedio_por_departamento (colegio_departamento);
