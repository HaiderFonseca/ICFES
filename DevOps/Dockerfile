# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual del directorio a /app dentro del contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecuta la aplicación cuando se inicie el contenedor
CMD ["python", "app.py"]