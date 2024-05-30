-- Crear la vista materializada de colegios
CREATE MATERIALIZED VIEW datos_colegios AS
SELECT
    periodo,
    colegio_nombre,
    MAX(colegio_area) AS colegio_area,
    MAX(colegio_bilingue) AS colegio_bilingue,
    MAX(colegio_calendario) AS colegio_calendario,
    MAX(colegio_caracter) AS colegio_caracter,
    MAX(colegio_departamento) AS colegio_departamento,
    MAX(colegio_genero) AS colegio_genero,
    MAX(colegio_jornada) AS colegio_jornada,
    MAX(colegio_municipio) AS colegio_municipio,
    MAX(colegio_naturaleza) AS colegio_naturaleza,
    COUNT(*) AS numero_estudiantes,
    AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, estudiante_fechanacimiento))) AS promedio_edad,
    COUNT(CASE WHEN estudiante_genero = 'M' THEN 1 END) AS numero_hombres,
    COUNT(CASE WHEN estudiante_genero = 'F' THEN 1 END) AS numero_mujeres,
    COUNT(CASE WHEN estudiante_municipio <> colegio_municipio THEN 1 END) AS estudiantes_fuera_municipio,
    AVG(puntaje_ingles) AS promedio_puntaje_ingles,
    AVG(puntaje_matematicas) AS promedio_puntaje_matematicas,
    AVG(puntaje_sociales_ciudadanas) AS promedio_puntaje_sociales_ciudadanas,
    AVG(puntaje_ciencias_naturales) AS promedio_puntaje_ciencias_naturales,
    AVG(puntaje_lectura_critica) AS promedio_puntaje_lectura_critica,
    AVG(puntaje_global) AS promedio_puntaje_global
FROM datos
GROUP BY
    periodo,
    colegio_nombre;

-- Crear índices para mejorar el rendimiento de las consultas
CREATE INDEX idx_vista_agrupada_periodo_colegio_nombre ON datos_colegios (periodo, colegio_nombre);
