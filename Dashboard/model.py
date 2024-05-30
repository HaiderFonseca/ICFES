import tensorflow as tf
import pandas as pd
import numpy as np


model = tf.keras.models.load_model('model.keras')

# Leer los nombres de las columnas desde el archivo
with open('model_variables.txt', 'r') as file:
    dummy_columns = [line.strip() for line in file]

categorical_columns = [
    'colegio_area', 'colegio_bilingue', 'colegio_calendario', 'colegio_caracter',
    'colegio_departamento', 'colegio_genero', 'colegio_jornada',
    'colegio_naturaleza', 'estudiante_genero', 'examen_periodo',
]

# Función para aplicar dummies asegurando el mismo conjunto de columnas
def apply_dummies_with_same_columns(df, dummy_columns):
    # Crear dummies para el nuevo conjunto de datos
    new_dummies = pd.get_dummies(df, columns=categorical_columns)
    
    # Agregar columnas faltantes con valor 0
    for col in dummy_columns:
        if col not in new_dummies:
            new_dummies[col] = 0
            
    # Asegurar que las columnas estén en el mismo orden
    new_dummies = new_dummies[dummy_columns]
    
    return new_dummies

def predict(
    colegio_area, colegio_bilingue, colegio_calendario, colegio_caracter,
    colegio_departamento, colegio_genero, colegio_jornada,
    colegio_naturaleza, estudiante_genero, examen_periodo,
):
    input_data = transform_input(
        colegio_area, colegio_bilingue, colegio_calendario, colegio_caracter,
        colegio_departamento, colegio_genero, colegio_jornada,
        colegio_naturaleza, estudiante_genero, examen_periodo, 
    )

    return model.predict(input_data).flatten()

def transform_input(
    colegio_area, colegio_bilingue, colegio_calendario, colegio_caracter,
    colegio_departamento, colegio_genero, colegio_jornada,
    colegio_naturaleza, estudiante_genero, examen_periodo,
):
    # Crear un DataFrame con los datos de entrada
    df = pd.DataFrame({
        'colegio_area': [colegio_area],
        'colegio_bilingue': [colegio_bilingue],
        'colegio_calendario': [colegio_calendario],
        'colegio_caracter': [colegio_caracter],
        'colegio_departamento': [colegio_departamento],
        'colegio_genero': [colegio_genero],
        'colegio_jornada': [colegio_jornada],
        'colegio_naturaleza': [colegio_naturaleza],
        'estudiante_genero': [estudiante_genero],
        'examen_periodo': [examen_periodo],
    })

    # Aplicar dummies asegurando el mismo conjunto de columnas
    dummies = apply_dummies_with_same_columns(df, dummy_columns)

    return dummies.to_numpy().astype(np.float32)

