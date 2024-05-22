# Configuración de S3 + Glue + Athena en AWS

## Crear buckets en S3

1. Crear un bucket que sirva para los datos de entrada del proceso ELT (Data Lake).
2. Crear una carpeta en el bucket de entrada llamada `data/`.
3. Crear un bucket que sirva para almacenar los resultados de las consultas ETL.

![S3 Buckets](./images/s3-buckets.png)

## Crear una tabla en Glue

1. Crear un workgroup llamado `icfes-workgroup` utilizando Athena SQL y el bucket de salida creado.
2. Crear una DataSource utilizando S3 Glue Data Catalog y asociar un nuevo Crawler.
3. Crear un Crawler llamado `icfes-crawler` que apunte a la carpeta `data/` del bucket de entrada.
4. Crear Database llamada `icfes-db` y asociar el Crawler creado.
5. Obtenga los datos siguiendo las instrucciones de la sección "Obtener los datos".
6. Ejecute el Crawler On-Demand y verifique que la tabla fue creada en la base de datos `icfes-db`.

![Glue Table](./images/glue-table.png)

## Obtener los datos

1. Usar el script `download_chunks.py` para descargar los datos paginados desde el API de `datos.gov.co`.
2. Manualmente subir todos los archivos CSV generados al bucket de entrada de S3.

![Download Chunks](./images/download-chunks.png)

## Crear una consulta en Athena


