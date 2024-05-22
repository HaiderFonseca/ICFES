# Este script descarga los datos de la URL proporcionada en chunks de 50000 filas y los guarda en archivos CSV en la carpeta "datos".
# Sigue la lógica de paginación de la API de Socrata. Documentación: https://support.socrata.com/hc/en-us/articles/202949268-How-to-query-more-than-1000-rows-of-a-dataset

import pandas as pd
import requests
import os
import io

# Configuración
base_url = "https://www.datos.gov.co/resource/kgxf-xxbe.csv"
limit = 50000
offset = 0
output_folder = "datos"
os.makedirs(output_folder, exist_ok=True)

# Contador de filas totales descargadas
total_rows_downloaded = 0

while True:
    # Construir URL con el offset y el limit
    url = f"{base_url}?$limit={limit}&$offset={offset}"
    print(f"Descargando datos desde el offset {offset}...")

    # Descargar datos
    response = requests.get(url)
    
    # Guardar en un DataFrame de pandas
    data = pd.read_csv(io.StringIO(response.text))
    
    # Verificar número de filas
    num_rows = data.shape[0]
    if num_rows == 0:
        print("No hay más datos para descargar.")
        break
    
    if num_rows != limit and num_rows != 0:
        print(f"Advertencia: se esperaban 50000 filas, pero se obtuvieron {num_rows}.")
    
    # Guardar a archivo CSV
    file_name = os.path.join(output_folder, f"data_offset_{offset}.csv")
    data.to_csv(file_name, index=False)
    print(f"Datos guardados en {file_name}.")

    # Actualizar contador de filas totales descargadas
    total_rows_downloaded += num_rows
    
    # Actualizar offset para la próxima iteración
    offset += limit
    
    # Detener si no se obtuvieron 50000 filas
    if num_rows < limit:
        print("Se descargó el último lote de datos.")
        break

print(f"Descarga completa. Total de datos descargados: {total_rows_downloaded} filas. Se esperan 7109704 filas en total.")
