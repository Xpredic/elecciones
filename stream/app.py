import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Proyección Electoral ONPE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# INICIALIZAR TODAS LAS VARIABLES DE SESIÓN
# ============================================
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0
if 'last_check' not in st.session_state:
    st.session_state.last_check = datetime.now()
if 'interval' not in st.session_state:
    st.session_state.interval = 60

# ============================================
# FUNCIÓN PARA VERIFICAR ACTUALIZACIÓN
# ============================================
def verificar_actualizacion():
    """Verifica si hay nuevos datos y los recarga"""
    update_file = "data/last_update.txt"
    
    if os.path.exists(update_file):
        mod_time = os.path.getmtime(update_file)
        if st.session_state.last_update != mod_time:
            st.session_state.last_update = mod_time
            st.cache_data.clear()
            return True
    return False

def toggle_auto_refresh():
    """Alterna el estado de auto-refresh"""
    st.session_state.auto_refresh = not st.session_state.auto_refresh
    if not st.session_state.auto_refresh:
        st.session_state.last_check = datetime.now()

def set_interval():
    """Actualiza el intervalo seleccionado"""
    st.session_state.interval = st.session_state.interval_selector

# ============================================
# SIDEBAR - CONTROLES
# ============================================
with st.sidebar:
    st.header("⚙️ Controles")
    
    # Botón de actualización manual
    if st.button("🔄 Actualizar Datos Manualmente", type="primary", use_container_width=True):
        if verificar_actualizacion():
            st.success("✅ Datos actualizados!")
            st.rerun()
        else:
            st.info("📊 No hay nuevos datos")
    
    st.markdown("---")
    
    # Auto-refresh con selector de intervalo
    auto_refresh = st.checkbox(
        "Auto-refresh", 
        value=st.session_state.auto_refresh,
        on_change=toggle_auto_refresh
    )
    
    if auto_refresh:
        # Selector de intervalo
        interval = st.selectbox(
            "Intervalo (segundos)", 
            [30, 60, 120, 300],
            index=[30, 60, 120, 300].index(st.session_state.interval),
            key="interval_selector",
            on_change=set_interval
        )
        
        # Mostrar temporizador
        placeholder = st.empty()
        
        # Calcular tiempo transcurrido
        tiempo_transcurrido = (datetime.now() - st.session_state.last_check).seconds
        
        if tiempo_transcurrido >= interval:
            st.session_state.last_check = datetime.now()
            st.session_state.refresh_counter += 1
            if verificar_actualizacion():
                placeholder.success(f"✅ Datos actualizados (ciclo {st.session_state.refresh_counter})")
                st.rerun()
            else:
                placeholder.info(f"🔄 Verificación {st.session_state.refresh_counter} - Sin cambios")
                st.rerun()
        else:
            segundos_restantes = interval - tiempo_transcurrido
            placeholder.info(f"⏳ Próxima actualización en {segundos_restantes} segundos")
    
    st.markdown("---")
    
    # Mostrar información de última actualización
    try:
        with open("data/last_update.txt", "r") as f:
            last_update_str = f.read().strip()
        st.caption(f"📅 Última descarga: {last_update_str}")
    except:
        st.caption(f"📅 Última descarga: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================
# CARGAR DATOS CON CACHE
# ============================================
@st.cache_data(ttl=300, show_spinner="Cargando datos...")
def cargar_datos_nacionales():
    """Carga los datos de proyección nacional"""
    try:
        df = pd.read_csv("data/tablas/proyeccion_nacional.csv")
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner="Cargando datos...")
def cargar_datos_completos():
    """Carga los datos completos de proyecciones"""
    try:
        df = pd.read_csv("data/tablas/proyecciones_completas.csv")
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()



# Configuración de la página
st.set_page_config(
    page_title="Proyección Electoral ONPE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aquí debes cargar tu DataFrame real desde CSV
proyeccion_nacional = pd.read_csv("../data/tablas/proyeccion_nacional.csv")
df_proyecciones = pd.read_csv("../data/tablas/proyecciones_completas.csv")
df_parametros_generales = pd.read_csv("../data/tablas/parametros_globales.csv")

porcentaje_Actual = df_parametros_generales['actasContabilizadas'][0]

# Título principal
st.title("📊 Proyección Nacional de Resultados Electorales")
st.markdown(f"### 📍 {porcentaje_Actual:.1f}% de actas contabilizadas a nivel nacional")
# Pie de subtítulo con última actualización
st.caption(f"📅 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Fuente: ONPE")

# Sidebar con información
with st.sidebar:
    st.header("⚙️ Configuración")
    st.markdown(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")
    st.header("📌 Metodología")
    st.markdown("""
    La proyección se calcula considerando:
    1. ✅ Último conteo por ubigeo
    2. ✅ Velocidad histórica de crecimiento
    3. ✅ Actas pendientes (100 - % actual)
    4. ✅ Ponderación por participación ciudadana
    """)


proyeccion_nacional = proyeccion_nacional.sort_values('votos_proyectados', ascending=False)

# Calcular totales
total_votos_actual = proyeccion_nacional['votos_actuales'].sum()
total_votos_proy = proyeccion_nacional['votos_proyectados'].sum()

# # === MÉTRICAS PRINCIPALES ===
# st.subheader("📈 Resumen Ejecutivo")

# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     st.metric(
#         label="🏆 Ganador Proyectado",
#         value=proyeccion_nacional.iloc[0]['candidato'].split(' - ')[0],
#         delta=f"{proyeccion_nacional.iloc[0]['votos_proyectados']:,.0f} votos"
#     )

# with col2:
#     diferencia = proyeccion_nacional.iloc[0]['votos_proyectados'] - proyeccion_nacional.iloc[1]['votos_proyectados']
#     st.metric(
#         label="📊 Ventaja sobre 2°",
#         value=f"{diferencia:,.0f}",
#         delta=f"{diferencia/total_votos_proy*100:.1f}% del total"
#     )

# with col3:
#     st.metric(
#         label="📈 Total Votos Proyectados",
#         value=f"{total_votos_proy:,.0f}",
#         delta=f"{(total_votos_proy - total_votos_actual):+,.0f}"
#     )

# with col4:
#     participacion = (total_votos_proy / 25000000) * 100  # Ajusta según población
#     st.metric(
#         label="🗳️ Participación Estimada",
#         value=f"{participacion:.1f}%",
#         delta="vs elecciones anteriores"
#     )

# st.markdown("---")

# # === TABLA DE PROYECCIONES ===
# st.subheader("📊 Proyección Nacional por Candidato")



# Preparar tabla para mostrar
tabla_mostrar = proyeccion_nacional.copy()
tabla_mostrar['% Proyectado'] = (tabla_mostrar['votos_proyectados'] / total_votos_proy * 100).round(2)
tabla_mostrar['Crecimiento'] = tabla_mostrar['votos_proyectados'] - tabla_mostrar['votos_actuales']
tabla_mostrar['Crecimiento %'] = (tabla_mostrar['Crecimiento'] / tabla_mostrar['votos_actuales'] * 100).round(1)

# Formatear columnas
tabla_mostrar['Votos Actuales'] = tabla_mostrar['votos_actuales'].apply(lambda x: f"{x:,.0f}")
tabla_mostrar['Votos Proyectados'] = tabla_mostrar['votos_proyectados'].apply(lambda x: f"{x:,.0f}")
tabla_mostrar['Crecimiento'] = tabla_mostrar['Crecimiento'].apply(lambda x: f"{x:+,.0f}")

# Mostrar tabla
columnas_mostrar = ['candidato', 'Votos Actuales', 'Votos Proyectados', 'Crecimiento', 'Crecimiento %', '% Proyectado']
st.dataframe(
    tabla_mostrar[columnas_mostrar],
    use_container_width=True,
    hide_index=True,
    column_config={
        'candidato': st.column_config.TextColumn('Candidato', width='large'),
        'Crecimiento %': st.column_config.NumberColumn('Crecimiento %', format='%.1f%%'),
        '% Proyectado': st.column_config.NumberColumn('% Proyectado', format='%.2f%%')
    }
)

st.markdown("---")

# === GRÁFICOS ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Candidatos Proyectados")
    
    top10 = proyeccion_nacional.head(10).copy()
    top10['candidato_short'] = top10['candidato'].str.split(' - ').str[0]
    
    fig = px.bar(
        top10,
        x='votos_proyectados',
        y='candidato_short',
        orientation='h',
        title='Votos Proyectados por Candidato',
        labels={'votos_proyectados': 'Votos Proyectados', 'candidato_short': 'Candidato'},
        color='votos_proyectados',
        color_continuous_scale='Viridis',
        text_auto='.0f'
    )
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Comparación: Actual vs Proyectado")
    
    top5 = proyeccion_nacional.head(5).copy()
    top5['candidato_short'] = top5['candidato'].str.split(' - ').str[0]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Votos Actuales',
        x=top5['candidato_short'],
        y=top5['votos_actuales'],
        marker_color='#3498db'
    ))
    fig.add_trace(go.Bar(
        name='Votos Proyectados',
        x=top5['candidato_short'],
        y=top5['votos_proyectados'],
        marker_color='#2ecc71'
    ))
    fig.update_layout(
        title='Comparación por Candidato (Top 5)',
        xaxis_title='Candidato',
        yaxis_title='Votos',
        barmode='group',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# === GRÁFICO DE DIFERENCIAS ===
st.subheader("📊 Diferencia entre Proyección Lineal y Ponderada")

top8 = proyeccion_nacional.head(8).copy()
top8['candidato_short'] = top8['candidato'].str.split(' - ').str[0]
top8['diferencia'] = top8['votos_proyectados'] - top8['votos_proyectados_lineal']

fig = px.bar(
    top8,
    x='candidato_short',
    y='diferencia',
    title='Impacto del Factor Participación Ciudadana',
    labels={'diferencia': 'Diferencia (votos)', 'candidato_short': 'Candidato'},
    color='diferencia',
    color_continuous_scale='RdBu',
    text_auto='.0f'
)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# === TABLA DE DETALLE POR UBIGEO ===
st.subheader("🗺️ Resultados por Ubigeo")

df_ubigeo = pd.DataFrame(df_proyecciones)
df_ubigeo = df_ubigeo.sort_values('votos_proyectados', ascending=False)

st.dataframe(
    df_ubigeo,
    use_container_width=True,
    hide_index=True,
    column_config={
        'ubicacion': 'Ubicación',
        'ganador': 'Ganador Proyectado',
        'votos_proyectados': st.column_config.NumberColumn('Votos Proyectados', format='%d'),
        'participacion': st.column_config.NumberColumn('Participación (%)', format='%.1f%%'),
        'actas_contabilizadas': st.column_config.NumberColumn('Actas (%)', format='%.1f%%')
    }
)

st.markdown("---")

# === MÉTRICAS ADICIONALES ===
st.subheader("📊 Análisis de Crecimiento")

col1, col2 = st.columns(2)

with col1:
    # Crecimiento por candidato
    crecimiento_df = proyeccion_nacional.head(8).copy()
    crecimiento_df['candidato_short'] = crecimiento_df['candidato'].str.split(' - ').str[0]
    crecimiento_df['crecimiento_pct'] = (crecimiento_df['votos_proyectados'] - crecimiento_df['votos_actuales']) / crecimiento_df['votos_actuales'] * 100
    
    fig = px.bar(
        crecimiento_df,
        x='candidato_short',
        y='crecimiento_pct',
        title='Crecimiento Proyectado por Candidato (%)',
        labels={'crecimiento_pct': 'Crecimiento (%)', 'candidato_short': 'Candidato'},
        color='crecimiento_pct',
        color_continuous_scale='RdYlGn',
        text_auto='.1f'
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Distribución de votos
    top8_dist = proyeccion_nacional.head(8).copy()
    top8_dist['candidato_short'] = top8_dist['candidato'].str.split(' - ').str[0]
    
    fig = px.pie(
        top8_dist,
        values='votos_proyectados',
        names='candidato_short',
        title='Distribución de Votos Proyectados (Top 8)',
        hole=0.4
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# === PIE DE PÁGINA ===
st.caption(f"📅 Datos actualizados al {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Fuente: ONPE - Proyección basada en datos oficiales")