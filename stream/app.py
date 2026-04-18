import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import json
import os
import glob
from datetime import datetime
import re

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = 'C:\\Users\\gamar\\Documents\\proyectos-git\\git-elecciones'
DATA_DIR = os.path.join(BASE_DIR, "data")

CARPETA_JSON = os.path.join(DATA_DIR, "json")
CARPETA_PARAMETROS = os.path.join(DATA_DIR, "parametros")
CARPETA_PARAMETROS_GLOBALES = os.path.join(DATA_DIR, "parametros_globales")
CARPETA_SALIDA = os.path.join(DATA_DIR, "tablas")

# Configurar página
st.set_page_config(page_title="Proyección Electoral", layout="wide")

# Título
st.title("📊 Proyección de Votos - Elecciones")

# Tu DataFrame (cargarlo o crearlo)
df = pd.read_csv(f'{CARPETA_SALIDA}\proyeccion_nacional.csv')  # o como lo tengas

# Gráfico principal
st.subheader("🏆 Proyección Nacional por Candidato")

# Seleccionar cantidad de candidatos a mostrar
top_n = st.slider("Mostrar top N candidatos:", 5, 20, 10)

top_candidatos = df.nlargest(top_n, 'votos_proyectados')

fig = px.bar(
    top_candidatos,
    x='candidato',
    y='votos_proyectados',
    text='intencion_proyectada',
    color='votos_proyectados',
    color_continuous_scale='Blues',
    title=f'Top {top_n} - Votos Proyectados'
)

fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(
    xaxis_tickangle=-45,
    height=500,
    showlegend=False,
    xaxis_title="Candidato",
    yaxis_title="Votos Proyectados"
)

st.plotly_chart(fig, use_container_width=True)

# Mostrar tabla
with st.expander("📋 Ver datos completos"):
    st.dataframe(df)