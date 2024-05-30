import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd

# Asegúrate de usar la ruta absoluta a tu archivo .env
dotenv_path = os.path.join(os.path.dirname(__file__), '../Despliegue/.env')
load_dotenv(dotenv_path=dotenv_path)

# Carga las variables de entorno
USER = os.getenv('USER_DB')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DBNAME = os.getenv('DBNAME')

# Verifica que las variables de entorno se hayan cargado correctamente
print(f"USER: {USER}, PASSWORD: {PASSWORD}, HOST: {HOST}, PORT: {PORT}, DBNAME: {DBNAME}")

# Conéctate a la base de datos
engine = psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

# Ejecuta la consulta y convierte el resultado en un DataFrame de pandas
cursor = engine.cursor()
query = "SELECT * FROM datos;"
df = pd.read_sql(query, engine)

# Muestra el DataFrame
print(df)


df.to_csv('datoscom.csv', index=False) 



