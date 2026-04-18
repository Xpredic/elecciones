import pandas as pd
import json
import os
import glob
from datetime import datetime
import re

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CARPETA_JSON = os.path.join(DATA_DIR, "json")
CARPETA_PARAMETROS = os.path.join(DATA_DIR, "parametros")
CARPETA_PARAMETROS_GLOBALES = os.path.join(DATA_DIR, "parametros_globales")
CARPETA_SALIDA = os.path.join(DATA_DIR, "tablas")

os.makedirs(CARPETA_SALIDA, exist_ok=True)

print("=" * 70)
print("🚀 PROCESAMIENTO DE DATOS ELECTORALES")
print("=" * 70)

# ============================================
# 1. CARGAR RESULTADOS ELECTORALES
# ============================================
def cargar_resultados(carpeta):
    todos_datos = []
    archivos = glob.glob(os.path.join(carpeta, "*.json"))
    
    print(f"📁 Resultados: {len(archivos)} archivos")
    
    if len(archivos) == 0:
        print("⚠️ No hay archivos de resultados en:", carpeta)
        return pd.DataFrame()
    
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            nombre_base = os.path.basename(archivo)
            nombre_sin_ext = nombre_base.replace('.json', '')
            
            # Extraer timestamp
            timestamp_match = re.search(r'_(\d{8}_\d{6})$', nombre_sin_ext)
            timestamp = timestamp_match.group(1) if timestamp_match else None
            nombre_sin_timestamp = nombre_sin_ext[:timestamp_match.start()] if timestamp_match else nombre_sin_ext
            
            # Detectar ámbito y ubicación
            ambito, ubicacion = None, None
            if 'ambito1' in nombre_sin_timestamp:
                ambito = 1
                partes = nombre_sin_timestamp.split('_')
                for i, parte in enumerate(partes):
                    if parte == 'ambito1' and i+1 < len(partes):
                        ubicacion = partes[i+1].zfill(6)
                        break
            elif 'ambito2' in nombre_sin_timestamp:
                ambito = 2
                region_match = re.search(r'region_\d+', nombre_sin_timestamp)
                if region_match:
                    ubicacion = region_match.group(0)
            
            for participante in data.get('data', []):
                fila = {
                    'ambito': ambito,
                    'ubicacion': ubicacion,
                    'timestamp_archivo': timestamp,
                    'nombre_agrupacion': participante.get('nombreAgrupacionPolitica'),
                    'nombre_candidato': participante.get('nombreCandidato'),
                    'total_votos_validos': participante.get('totalVotosValidos', 0),
                    'porcentaje_votos_validos': participante.get('porcentajeVotosValidos', 0),
                    'porcentaje_votos_emitidos': participante.get('porcentajeVotosEmitidos', 0),
                }
                todos_datos.append(fila)
        except Exception as e:
            print(f"⚠️ Error en archivo {archivo}: {e}")
    
    return pd.DataFrame(todos_datos)

# ============================================
# 2. CARGAR PARÁMETROS
# ============================================
def cargar_parametros(carpeta, tipo):
    todos_parametros = []
    archivos = glob.glob(os.path.join(carpeta, "*.json"))
    
    print(f"📁 {tipo}: {len(archivos)} archivos")
    
    if len(archivos) == 0:
        print(f"⚠️ No hay archivos de {tipo} en:", carpeta)
        return pd.DataFrame()
    
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'data' in data and isinstance(data['data'], dict):
                params = data['data']
                
                nombre_base = os.path.basename(archivo)
                nombre_sin_ext = nombre_base.replace('.json', '')
                
                # Extraer ubicación del nombre del archivo
                ubicacion = None
                if 'ambito1' in nombre_sin_ext:
                    partes = nombre_sin_ext.split('_')
                    for i, parte in enumerate(partes):
                        if parte == 'ambito1' and i+1 < len(partes):
                            ubicacion = partes[i+1].zfill(6)
                            break
                elif 'ambito2' in nombre_sin_ext:
                    region_match = re.search(r'region_\d+', nombre_sin_ext)
                    if region_match:
                        ubicacion = region_match.group(0)
                
                # Si no se extrajo del nombre, intentar del contenido
                if ubicacion is None:
                    ubicacion = params.get('idUbigeoDepartamento', None)
                    if ubicacion:
                        ubicacion = str(ubicacion).zfill(6)
                
                params['ubicacion'] = ubicacion
                todos_parametros.append(params)
        except Exception as e:
            print(f"⚠️ Error en archivo {archivo}: {e}")
    
    df = pd.DataFrame(todos_parametros)
    
    # Verificar si la columna 'ubicacion' existe
    if 'ubicacion' not in df.columns:
        print(f"⚠️ No se encontró columna 'ubicacion' en {tipo}")
        print(f"   Columnas disponibles: {df.columns.tolist()}")
    else:
        print(f"✅ {tipo}: {len(df)} registros con ubicacion")
    
    return df

# ============================================
# 3. FUNCIÓN DE PROYECCIÓN
# ============================================
def proyectar_votos(df_ubigeo, candidato):
    df_cand = df_ubigeo[df_ubigeo['nombre_agrupacion'] == candidato].copy()
    if len(df_cand) == 0:
        return None
    
    df_cand = df_cand.sort_values('timestamp_archivo')
    ultimo = df_cand.iloc[-1]
    
    votos_actuales = ultimo['total_votos_validos']
    actas_actual = ultimo.get('actasContabilizadas', 0)
    
    if actas_actual == 0:
        return None
    
    if len(df_cand) >= 2:
        votos_anteriores = df_cand.iloc[-2]['total_votos_validos']
        actas_anteriores = df_cand.iloc[-2].get('actasContabilizadas', 0)
        if actas_anteriores > 0:
            delta_votos = votos_actuales - votos_anteriores
            delta_actas = actas_actual - actas_anteriores
            velocidad = delta_votos / delta_actas if delta_actas > 0 else 0
        else:
            velocidad = 0
    else:
        velocidad = 0
    
    actas_pendientes = 100 - actas_actual
    votos_proyectados_lineal = votos_actuales + (velocidad * actas_pendientes)
    
    participacion = ultimo.get('participacionCiudadana', 50)
    factor = participacion / 100 if participacion > 0 else 0.5
    votos_proyectados = votos_proyectados_lineal * (0.7 + 0.3 * factor)
    
    return {
        'candidato': candidato,
        'ubicacion': ultimo['ubicacion'],
        'votos_actuales': int(votos_actuales),
        'votos_proyectados': int(votos_proyectados),
        'actas_contabilizadas': actas_actual,
        'participacion': participacion
    }

def proyectar_todos(df):
    proyecciones = []
    
    if df.empty:
        print("⚠️ DataFrame vacío, no se pueden calcular proyecciones")
        return pd.DataFrame()
    
    # Verificar columnas necesarias
    if 'nombre_agrupacion' not in df.columns:
        print("❌ Columna 'nombre_agrupacion' no encontrada")
        return pd.DataFrame()
    
    candidatos = df[~df['nombre_agrupacion'].str.contains('BLANCO|NULO', case=False, na=False)]['nombre_agrupacion'].unique()
    print(f"📊 Candidatos encontrados: {len(candidatos)}")
    
    for ubicacion in df['ubicacion'].unique():
        if pd.isna(ubicacion):
            continue
        df_ubi = df[df['ubicacion'] == ubicacion]
        for candidato in candidatos:
            resultado = proyectar_votos(df_ubi, candidato)
            if resultado:
                proyecciones.append(resultado)
    
    return pd.DataFrame(proyecciones)

# ============================================
# 4. EJECUCIÓN PRINCIPAL
# ============================================
print("\n📂 Cargando datos...")
df_resultados = cargar_resultados(CARPETA_JSON)
df_parametros = cargar_parametros(CARPETA_PARAMETROS, "Parámetros")

# Cargar parámetros globales
df_parametros_globales = pd.DataFrame()
archivos_globales = glob.glob(os.path.join(CARPETA_PARAMETROS_GLOBALES, "*.json"))
if archivos_globales:
    print(f"📁 Parámetros globales: {len(archivos_globales)} archivos")
    for archivo in archivos_globales:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'data' in data:
                df_parametros_globales = pd.DataFrame([data['data']] if isinstance(data['data'], dict) else data['data'])
        except Exception as e:
            print(f"⚠️ Error cargando globales: {e}")
else:
    print("⚠️ No hay archivos de parámetros globales")

# Verificar si hay datos para unir
if df_resultados.empty:
    print("❌ No hay datos de resultados para procesar")
    exit(1)

if df_parametros.empty:
    print("⚠️ No hay parámetros, usando solo resultados")
    df_completo = df_resultados.copy()
else:
    # Unir resultados con parámetros
    print("\n🔗 Uniendo datos...")
    df_resultados['ubicacion'] = df_resultados['ubicacion'].astype(str)
    if 'ubicacion' in df_parametros.columns:
        df_parametros['ubicacion'] = df_parametros['ubicacion'].astype(str)
        df_completo = df_resultados.merge(df_parametros, on='ubicacion', how='left')
    else:
        print("⚠️ No se puede unir: falta columna 'ubicacion' en parámetros")
        df_completo = df_resultados.copy()

df_completo = df_completo.sort_values(['ubicacion', 'timestamp_archivo'])

# Calcular proyecciones
print("\n🚀 Calculando proyecciones...")
df_proyecciones = proyectar_todos(df_completo)

if df_proyecciones.empty:
    print("❌ No se generaron proyecciones")
    exit(1)

# Proyección nacional
proyeccion_nacional = df_proyecciones.groupby('candidato').agg({
    'votos_actuales': 'sum',
    'votos_proyectados': 'sum'
}).reset_index()
proyeccion_nacional = proyeccion_nacional.sort_values('votos_proyectados', ascending=False)
proyeccion_nacional['porcentaje'] = (proyeccion_nacional['votos_proyectados'] / proyeccion_nacional['votos_proyectados'].sum() * 100).round(2)

# ============================================
# 5. GUARDAR ARCHIVOS
# ============================================
print("\n💾 Guardando archivos...")

proyeccion_nacional.to_csv(os.path.join(CARPETA_SALIDA, "proyeccion_nacional.csv"), index=False, encoding='utf-8')
df_proyecciones.to_csv(os.path.join(CARPETA_SALIDA, "proyecciones_completas.csv"), index=False, encoding='utf-8')

if not df_parametros_globales.empty:
    df_parametros_globales.to_csv(os.path.join(CARPETA_SALIDA, "parametros_globales.csv"), index=False, encoding='utf-8')

print(f"\n✅ Archivos guardados en: {CARPETA_SALIDA}")
print(f"   - proyeccion_nacional.csv ({len(proyeccion_nacional)} candidatos)")
print(f"   - proyecciones_completas.csv ({len(df_proyecciones)} registros)")

# Mostrar top 5
print("\n" + "=" * 70)
print("📊 TOP 5 PROYECCIÓN NACIONAL")
print("=" * 70)
for _, row in proyeccion_nacional.head(5).iterrows():
    print(f"{row['candidato'][:45]:<45} {row['votos_proyectados']:>15,} votos ({row['porcentaje']:.2f}%)")

print("\n✅ Proceso completado!")

