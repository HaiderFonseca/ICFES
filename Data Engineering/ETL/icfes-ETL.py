import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import re

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node ICFES AWS Glue Data Catalog
ICFESAWSGlueDataCatalog_node1716492193408 = glueContext.create_dynamic_frame.from_catalog(database="icfes-db", table_name="data", transformation_ctx="ICFESAWSGlueDataCatalog_node1716492193408")

# Apply ResolveChoice on punt_ingles and punt_matematicas columns
ResolveChoice_node = ResolveChoice.apply(frame=ICFESAWSGlueDataCatalog_node1716492193408, specs=[("punt_ingles", "cast:double"), ("punt_matematicas", "cast:double")], transformation_ctx="ResolveChoice_node")

# Script generated for node Drop Fields
DropFields_node1716495601898 = DropFields.apply(frame=ResolveChoice_node, paths=["desemp_ingles", "fami_personashogar", "fami_tieneautomovil", "fami_tienecomputador", "fami_tieneinternet", "fami_tienelavadora", "fami_estratovivienda", "fami_educacionpadre", "fami_educacionmadre", "fami_cuartoshogar", "estu_privado_libertad", "estu_pais_reside", "estu_nacionalidad", "estu_mcpio_presentacion", "estu_estudiante", "estu_estadoinvestigacion", "estu_depto_presentacion", "estu_cod_reside_depto", "estu_cod_reside_mcpio", "estu_cod_depto_presentacion", "estu_cod_mcpio_presentacion", "cole_sede_principal", "cole_nombre_sede", "cole_codigo_icfes", "cole_cod_dane_establecimiento", "cole_cod_dane_sede", "cole_cod_depto_ubicacion", "cole_cod_mcpio_ubicacion", "estu_tipodocumento", "estu_consecutivo"], transformation_ctx="DropFields_node1716495601898")

# Script generated for node Change Schema
ChangeSchema_node1716498355525 = ApplyMapping.apply(frame=DropFields_node1716495601898, mappings=[("periodo", "long", "periodo", "string"), ("cole_area_ubicacion", "string", "colegio_area", "string"), ("cole_bilingue", "string", "colegio_bilingue", "string"), ("cole_calendario", "string", "colegio_calendario", "string"), ("cole_caracter", "string", "colegio_caracter", "string"), ("cole_depto_ubicacion", "string", "colegio_departamento", "string"), ("cole_genero", "string", "colegio_genero", "string"), ("cole_jornada", "string", "colegio_jornada", "string"), ("cole_mcpio_ubicacion", "string", "colegio_municipio", "string"), ("cole_naturaleza", "string", "colegio_naturaleza", "string"), ("cole_nombre_establecimiento", "string", "colegio_nombre", "string"), ("estu_depto_reside", "string", "estudiante_departamento", "string"), ("estu_fechanacimiento", "string", "estudiante_fechanacimiento", "date"), ("estu_genero", "string", "estudiante_genero", "string"), ("estu_mcpio_reside", "string", "estudiante_municipio", "string"), ("punt_ingles", "double", "puntaje_ingles", "double"), ("punt_matematicas", "double", "puntaje_matematicas", "double"), ("punt_sociales_ciudadanas", "double", "puntaje_sociales_ciudadanas", "double"), ("punt_c_naturales", "double", "puntaje_ciencias_naturales", "double"), ("punt_lectura_critica", "double", "puntaje_lectura_critica", "double"), ("punt_global", "double", "puntaje_global", "double")], transformation_ctx="ChangeSchema_node1716498355525")

# Script generated for node Filter
Filter_node1716498358596 = Filter.apply(frame=ChangeSchema_node1716498355525, f=lambda row: (row["puntaje_global"] >= 0 and row["puntaje_global"] <= 500 and row["puntaje_ingles"] >= 0 and row["puntaje_ingles"] <= 100 and row["puntaje_matematicas"] >= 0 and row["puntaje_matematicas"] <= 100 and row["puntaje_sociales_ciudadanas"] >= 0 and row["puntaje_sociales_ciudadanas"] <= 100 and row["puntaje_ciencias_naturales"] >= 0 and row["puntaje_ciencias_naturales"] <= 100 and row["puntaje_lectura_critica"] >= 0 and row["puntaje_lectura_critica"] <= 100), transformation_ctx="Filter_node1716498358596")

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1716498362915 = glueContext.write_dynamic_frame.from_catalog(frame=Filter_node1716498358596, database="icfes-db", table_name="clean_data", transformation_ctx="AWSGlueDataCatalog_node1716498362915")

job.commit()