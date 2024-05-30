from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from os import path
from dotenv import load_dotenv
from model import predict
import psycopg2
import os
import json
import random

app = Dash(__name__, external_stylesheets = [path.join('assets', 'styles.css')])
app.title = "Resultados ICFES"

load_dotenv(dotenv_path='.env')
USER=os.getenv('USER_DB')
PASSWORD=os.getenv('PASSWORD')
HOST=os.getenv('HOST')
PORT=os.getenv('PORT')
DBNAME=os.getenv('DBNAME')

engine = psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)
cursor = engine.cursor()

# Views column renaming
rename_views = {
    'promedio_puntaje_ingles': 'Inglés',
    'promedio_puntaje_matematicas': 'Matemáticas',
    'promedio_puntaje_sociales_ciudadanas': 'Ciencias Sociales',
    'promedio_puntaje_ciencias_naturales': 'Ciencias Naturales',
    'promedio_puntaje_lectura_critica': 'Lectura Crítica',
    'promedio_puntaje_global': 'Total',

    'colegio_departamento': 'Departamento',
    'colegio_nombre': 'Colegio',
    'colegio_calendario': 'Calendario',
    'colegio_naturaleza': 'Naturaleza',
    'colegio_area': 'Área',
}

categorical_options = json.load(open('assets/categories.json', 'r'))
geojson = json.load(open('assets/colombia_departamentos.geojson', 'r'))

query_map = "SELECT * FROM puntajes_promedio_por_departamento;"
df_map = pd.read_sql(query_map, engine).rename(columns=rename_views)

@app.callback(
    Output('graph-map', 'figure'),
    [Input('map-area-dropdown', 'value')]
)
def update_map(selected_area):
    fig = px.choropleth(
        df_map,
        geojson=geojson,
        featureidkey='properties.NOMBRE_DPT',
        locations="Departamento",
        color=selected_area,
        hover_name="Departamento",
        color_continuous_scale="YlGn",
        hover_data={'Total': True, 'Inglés': True, 'Matemáticas': True, 'Ciencias Sociales': True, 'Ciencias Naturales': True, 'Lectura Crítica': True},
        width=800,
        height=800,
        projection="mercator",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(autosize=True)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(coloraxis_colorbar=dict(xanchor='left', x=0, len=0.5))
    return fig


query_colegios = "SELECT * FROM datos_colegios;"
df_colegios = pd.read_sql(query_colegios, engine).rename(columns=rename_views)
df_colegios['periodo'] = df_colegios['periodo'].astype(str).str[:4].astype(int)
df_colegios['Colegio'] = df_colegios['Colegio'].str.title()
df_colegios = df_colegios.sort_values(by=['periodo', 'Total'], ascending=[True, False])
df_colegios['Rank'] = df_colegios.groupby('periodo').cumcount() + 1
all_colegios = df_colegios['Colegio'].unique()

@app.callback(
    Output('graph-ranking', 'figure'),
    [Input('ranking-colegio-dropdown', 'value')]
)
def update_bump_chart(selected_colegios):
    filtered_df = df_colegios[df_colegios['Colegio'].isin(selected_colegios)]
    fig = px.line(filtered_df, x='periodo', y='Rank', color='Colegio', hover_data=['Total'])
    fig.update_yaxes(title_text='Ranking', autorange='reversed')
    fig.update_xaxes(categoryorder='total ascending')
    fig.update_layout(margin={"r":0,"t": 0,"l":0,"b":0})
    fig.update_traces(mode='markers+lines', marker=dict(size=10), line=dict(width=2), showlegend=False)
    fig.update_layout(width=600, height=400)
    return fig


demographics_options = [
    {'label': 'Calendario Académico', 'value': 'Calendario'},
    {'label': 'Naturaleza (Público/Privado)', 'value': 'Naturaleza'},
    {'label': 'Área Geográfica', 'value': 'Área'},
]

demographics_dfs = {
    'Calendario': pd.read_sql("SELECT * FROM puntajes_promedio_por_calendario;", engine).rename(columns=rename_views).replace('', 'Desconocido'),
    'Naturaleza': pd.read_sql("SELECT * FROM puntajes_promedio_por_naturaleza;", engine).rename(columns=rename_views).replace('', 'Desconocido'),
    'Área': pd.read_sql("SELECT * FROM puntajes_promedio_por_area;", engine).rename(columns=rename_views).replace('', 'Desconocido'),
}

@app.callback(
    Output('graph-demograficos', 'figure'),
    [Input('demograficos-dropdown', 'value')]
)
def update_demographics_chart(selected_demographics):
    if selected_demographics is None:
        return {
            'data': [],
            'layout': {
                'title': 'Selecciona un grupo demográfico para visualizar los resultados',
            }
        }
        
    df = demographics_dfs[selected_demographics]
    fig = px.bar(df, x=selected_demographics, y='Total')
    fig.update_layout(width=600, height=300)
    return fig


def create_gauge_figure(display_value, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = display_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {'axis': {'range': [0, 100], 'ticks': 'outside', 'dtick': 10}, 'bar': {'color': '#386fa4'}},
        number={'suffix': "", 'font': {'color': '#386fa4'}},  # Color del número
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Color de fondo del lienzo
        plot_bgcolor='rgba(0,0,0,0)',   # Color de fondo del gráfico
        width=220,  # Ancho de la gráfica
        height=220,  # Altura de la gráfica
        margin={"t": 0, "b": 0, "l": 0, "r": 0},  # Ajustar los márgenes
        font={"color": '#386fa4'},
    )
    return fig

@callback(
    [
        Output(component_id='gauge-model-ingles', component_property='figure'),
        Output(component_id='gauge-model-math', component_property='figure'),
        Output(component_id='gauge-model-sociales', component_property='figure'),
        Output(component_id='gauge-model-ciencias', component_property='figure'),
        Output(component_id='gauge-model-lectura', component_property='figure'),
        Output(component_id='gauge-model-total', component_property='figure'),
    ],
    [
        # Dropdowns
        Input(component_id='area-dropdown', component_property='value'),
        Input(component_id='bilingue-dropdown', component_property='value'),
        Input(component_id='calendario-dropdown', component_property='value'),
        Input(component_id='caracter-dropdown', component_property='value'),
        Input(component_id='departamento-dropdown', component_property='value'),
        Input(component_id='genero-dropdown', component_property='value'),
        Input(component_id='jornada-dropdown', component_property='value'),
        Input(component_id='naturaleza-dropdown', component_property='value'),
        Input(component_id='genero-est-dropdown', component_property='value'),
        Input(component_id='periodo-dropdown', component_property='value'),
    ]
)
def create_gauge_figure_model(
    colegio_area, colegio_bilingue, colegio_calendario, colegio_caracter,
    colegio_departamento, colegio_genero, colegio_jornada,
    colegio_naturaleza, estudiante_genero, examen_periodo,  
):
    if any([
        colegio_area is None, 
        colegio_bilingue is None, 
        colegio_calendario is None, 
        colegio_caracter is None,
        colegio_departamento is None, 
        colegio_genero is None, 
        colegio_jornada is None, 
        colegio_naturaleza is None, 
        estudiante_genero is None, 
        examen_periodo is None,
    ]):
        probabilities = np.zeros((5,))

    else:
        probabilities = predict(
            colegio_area, colegio_bilingue, colegio_calendario, colegio_caracter,
            colegio_departamento, colegio_genero, colegio_jornada,
            colegio_naturaleza, estudiante_genero, examen_periodo, 
        )

    puntaje_ingles = probabilities[0] * 100
    puntaje_matematicas = probabilities[1] * 100
    puntaje_sociales = probabilities[2] * 100
    puntaje_ciencias = probabilities[3] * 100
    puntaje_lectura = probabilities[4] * 100
    puntaje_total = (puntaje_matematicas*3 + puntaje_lectura*3 + puntaje_ciencias*3 + puntaje_sociales*3 + puntaje_ingles) / 13 * 5

    return (
        create_gauge_figure(round(puntaje_ingles), "Inglés"),
        create_gauge_figure(round(puntaje_matematicas), "Matemáticas"),
        create_gauge_figure(round(puntaje_sociales), "Ciencias Sociales"),
        create_gauge_figure(round(puntaje_ciencias), "Ciencias Naturales"),
        create_gauge_figure(round(puntaje_lectura), "Lectura Crítica"),
        create_overall_score_gauge(round(puntaje_total, 0)),
    )


def create_overall_score_gauge(value):
    fig = go.Figure(go.Indicator(
        mode = "number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Puntaje ICFES"},
        number={'suffix': "", 'font': {'color': '#386fa4'}},  # Color del número
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Color de fondo del lienzo
        plot_bgcolor='rgba(0,0,0,0)',   # Color de fondo del gráfico
        width=220,  # Ancho de la gráfica
        height=220,  # Altura de la gráfica
        margin={"t": 0, "b": 0, "l": 0, "r": 0},  # Ajustar los márgenes
        font={"color": '#386fa4'},
    )
    return fig


app.layout = html.Div([
    html.Header([
        html.Section([
            html.H1("PredICFES: Visualizando el futuro académico"),
            html.P("Herramienta analítica para visualizar Factores, Comparaciones Regionales y Tendencias en el puntaje ICFES."),
        ], className="header-title"),
        html.Section([
            html.Img(src=path.join('assets', 'logo.png'), alt="ICFES Logo"),
        ], className="header-logo"),
    ], className="header-container"),
    html.Main([
        html.Section([
            html.Div([
                html.H2("Resultados por Departamento", style={'marginTop': '10px'}),
                html.Div([
                    dcc.Graph(id="graph-map"),
                    html.Div([
                        html.P("Selecciona el área de la prueba ICFES que deseas visualizar:", style={'fontSize': '1.2em', 'textAlign': 'left'}),
                        dcc.RadioItems(
                            id='map-area-dropdown',
                            options=[
                                {'label': ' Total', 'value': 'Total'},
                                {'label': ' Matemáticas', 'value': 'Matemáticas'},
                                {'label': ' Ciencias Naturales', 'value': 'Ciencias Naturales'},
                                {'label': ' Ciencias Sociales', 'value': 'Ciencias Sociales'},
                                {'label': ' Lectura Crítica', 'value': 'Lectura Crítica'},
                                {'label': ' Inglés', 'value': 'Inglés'},
                            ],
                            value='Total',
                            labelStyle={'display': 'block', 'margin': '10px', },
                        ),
                    ], style={'display': 'flex', 'gap': '20px', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'marginRight': '20px'}),
                ], style={'display': 'grid', 'gap': '10px', 'gridTemplateColumns': '1fr 200px'}),
                html.P("Visualiza el puntaje promedio obtenido por los estudiantes de cada departamento del país."),
            ], className="card", style={'height': '100%'}),
            html.Div([
                html.Div([
                    html.H2("Evolución del Ranking de Colegios"),
                    dcc.Dropdown(
                        id='ranking-colegio-dropdown',
                        options=[{'label': colegio, 'value': colegio} for colegio in all_colegios],
                        value=random.choices(all_colegios, k=1),
                        multi=True 
                    ),
                    dcc.Graph(id="graph-ranking"),
                    html.P("Muestra el cambio en el Ranking del conjunto de colegios seleccionados a lo largo del tiempo."),
                ], className="card", style={'width': '100%'}),  
                html.Div([
                    html.H2("Comparaciones Demográficas"),
                    dcc.Dropdown(
                        id='demograficos-dropdown',
                        options=demographics_options,
                        value=demographics_options[0]['value'],
                    ),
                    dcc.Graph(id="graph-demograficos"),
                    html.P("Permite comparar el desempeño global de distintos grupos demográficos."),
                ], className="card", style={'width': '100%'}),  
            ], style={'height': '100%', 'display': 'grid', 'gap': '20px', 'gridAutoFlow': 'row'}),
        ], className="main-graphs", style={'display': 'grid', 'gap': '20px', 'gridTemplateColumns': '6fr 4fr'}),
        html.Section([
            html.H2("Predicción de Resultados por Competencias"),
            html.Div([
                html.Section([
                    html.Section([
                        html.H3("Información del Colegio", style={'color': 'var(--Primary)', 'margin-bottom': '10px'}),
                        html.Div([
                            html.Div([
                                html.P("Área:"), 
                                dcc.Dropdown(
                                    id='area-dropdown',
                                    options=[item for item in categorical_options['colegio_area']],
                                    placeholder="Selecciona el área del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Bilingüe:"), 
                                dcc.Dropdown(
                                    id='bilingue-dropdown',
                                    options=[item for item in categorical_options['colegio_bilingue']],
                                    placeholder="Selecciona si el colegio es bilingüe...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Calendario:"), 
                                dcc.Dropdown(
                                    id='calendario-dropdown',
                                    options=[item for item in categorical_options['colegio_calendario']],
                                    placeholder="Selecciona el calendario del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Carácter:"), 
                                dcc.Dropdown(
                                    id='caracter-dropdown',
                                    options=[item for item in categorical_options['colegio_caracter']],
                                    placeholder="Selecciona el carácter del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Departamento:"), 
                                dcc.Dropdown(
                                    id='departamento-dropdown',
                                    options=[item for item in categorical_options['colegio_departamento']],
                                    placeholder="Selecciona el departamento del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Género:"), 
                                dcc.Dropdown(
                                    id='genero-dropdown',
                                    options=[item for item in categorical_options['colegio_genero']],
                                    placeholder="Selecciona el género del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Jornada:"), 
                                dcc.Dropdown(
                                    id='jornada-dropdown',
                                    options=[item for item in categorical_options['colegio_jornada']],
                                    placeholder="Selecciona la jornada del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                            html.Div([
                                html.P("Naturaleza:"), 
                                dcc.Dropdown(
                                    id='naturaleza-dropdown',
                                    options=[item for item in categorical_options['colegio_naturaleza']],
                                    placeholder="Selecciona la naturaleza del colegio...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                            
                        ], style={'display': 'grid', 'gap': '10px'}),
                    ], style={'padding': '20px', 'display': 'flex', 'flex-direction': 'column', 'justifyContent': 'space-between', 'gap': '5px'}),
                    html.Section([
                        html.H3("Información del Estudiante", style={'color': 'var(--Primary)', 'margin-bottom': '10px'}),
                        html.Div([
                            html.Div([
                                html.P("Género:"), 
                                dcc.Dropdown(
                                    id='genero-est-dropdown',
                                    options=[item for item in categorical_options['estudiante_genero']],
                                    placeholder="Selecciona el género del estudiante...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                        ], style={'display': 'grid', 'gap': '10px'}),
                    ], style={'padding': '20px', 'display': 'flex', 'flex-direction': 'column', 'justifyContent': 'space-between', 'gap': '5px'}),
                    html.Section([
                        html.H3("Período de Evaluación", style={'color': 'var(--Primary)', 'margin-bottom': '10px'}),
                        html.Div([
                            html.Div([
                                html.P("Período:"), 
                                dcc.Dropdown(
                                    id='periodo-dropdown',
                                    options=[item for item in categorical_options['examen_periodo']],
                                    placeholder="Selecciona el periodo de evaluación...",
                                ),
                            ], style={'display': 'grid', 'justifyContent': 'space-between', 'gap': '5px', 'gridTemplateColumns': '140px 1fr', 'alignItems': 'center'}),
                        ], style={'display': 'grid', 'gap': '10px'}),
                    ], style={'padding': '20px', 'display': 'flex', 'flex-direction': 'column', 'justifyContent': 'space-between', 'gap': '5px'}),
                ], style={'width': '100%', 'padding': '10px 10px', 'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'flex-direction': 'column'}),
                html.Section([
                    html.Div([
                        html.Div([
                            dcc.Graph(id="gauge-model-math"),
                            dcc.Graph(id="gauge-model-ciencias"),
                            dcc.Graph(id="gauge-model-sociales"),
                            dcc.Graph(id="gauge-model-lectura"),
                            dcc.Graph(id="gauge-model-total"),
                            dcc.Graph(id="gauge-model-ingles"),
                        ], className="gauge-container"),
                        html.Div([
                            html.H3("Predicción de Resultados ICFES", style={'textAlign': 'center'}),
                            html.P("Este modelo predice los resultados de un estudiante en las pruebas ICFES Saber 11 basado en la información ingresada. Utilice los controles para ajustar los valores y obtener una predicción."),
                        ], style={'padding': '0 64px'}),
                    ], className="model-container"),
                ]),
            ], className="ml-container"),
        ], className="card main-models-container"),
    ], className="main-container"),
    html.Footer([
        html.P("Desarrollado por Haider Fonseca, Daniela Arenas y Sebastian Urrea"),
        html.P("Analítica Computacional para la Toma de Decisiones - Universidad de los Andes - 2024"),
    ], className="footer-container"),
], className="root-container")


if __name__ == '__main__':
    app.run_server(host = "localhost", port=8050, debug=True)
