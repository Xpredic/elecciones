import pandas as pd
import json
import os
import glob
from datetime import datetime
import re

# CARPETAS BASE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = 'C:/Users/gamar/Documents/proyectos-git/git-elecciones'
DATA_DIR = os.path.join(BASE_DIR, "data")

CARPETA_JSON = os.path.join(DATA_DIR, "json")
CARPETA_PARAMETROS = os.path.join(DATA_DIR, "parametros")
CARPETA_PARAMETROS_GLOBALES = os.path.join(DATA_DIR, "parametros_globales")
CARPETA_SALIDA = os.path.join(DATA_DIR, "tablas")


print("="*60)
print("INICIO DE LA LECTURA - JSON")
print("="*60)

try:
    json_files = os.listdir(CARPETA_JSON)
except FileNotFoundError:
    print(f"Error: No se encontró la carpeta {CARPETA_JSON}")

def process_json(file_path):
    registros_procesados = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        datos_raw = data.get('data', [])

        nombre_base = os.path.basename(file_path)
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
            partes = nombre_sin_timestamp.split('_')
            for i, parte in enumerate(partes):
                if parte == 'ambito2' and i+1 < len(partes):
                    ubicacion = partes[i+1].zfill(6)
                    break

        for participante in datos_raw:
            fila = {
                    'ambito': ambito,
                    'ubicacion': ubicacion,
                    'timestamp_json': timestamp,
                    'fecha_procesamiento': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'codigo_agrupacion': participante.get('codigoAgrupacionPolitica'),
                    'nombre_agrupacion': participante.get('nombreAgrupacionPolitica'),
                    'nombre_candidato': participante.get('nombreCandidato'),
                    'dni_candidato': participante.get('dniCandidato'),
                    'total_votos_validos': participante.get('totalVotosValidos', 0),
                    'porcentaje_votos_validos': participante.get('porcentajeVotosValidos', 0),
                    'porcentaje_votos_emitidos': participante.get('porcentajeVotosEmitidos', 0),
                    'archivo_origen': nombre_base
                }
            registros_procesados.append(fila)

    except Exception as e:
            print(f"⚠️ Error en archivo {file_path}: {e}")

    return registros_procesados

data_enriquecida = []
for file in json_files:
    full_path = os.path.join(CARPETA_JSON, file)
    if not os.path.exists(full_path):
        print(f"Archivo no encontrado: {file}")
        continue
    lecture = process_json(full_path)
    data_enriquecida.append(lecture)

# Aplanar la lista de listas
if isinstance(data_enriquecida, list) and len(data_enriquecida) > 0:
    if isinstance(data_enriquecida[0], list):
        datos_planos = [item for sublist in data_enriquecida for item in sublist]
    else:
        datos_planos = data_enriquecida
else:
    datos_planos = data_enriquecida

# Crear DataFrame
df = pd.DataFrame(datos_planos)

# Ver resultado
print(f"✅ DataFrame creado: {df.shape[0]} filas, {df.shape[1]} columnas")
print(df.head())
print(f"\n✅ Tabla creada: {df.shape[0]} filas, {df.shape[1]} columnas")
print(f"\n📊 Columnas disponibles:")
print(df.columns.tolist())

print("="*60)
print("FIN DE LA LECTURA - JSON")
print("="*60)

print("="*60)
print("INICIO DE LA LECTURA - PARAMETROS")
print("="*60)

try:
    json_files = os.listdir(CARPETA_PARAMETROS)
except FileNotFoundError:
    print(f"Error: No se encontró la carpeta {CARPETA_PARAMETROS}")

def process_json_parametros(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        datos_raw = data['data']

        nombre_base = os.path.basename(file_path)
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
            partes = nombre_sin_timestamp.split('_')
            for i, parte in enumerate(partes):
                if parte == 'ambito2' and i+1 < len(partes):
                    ubicacion = partes[i+1].zfill(6)
                    break

        fila = {
                    'ambito': ambito,
                    'ubicacion': ubicacion,
                    'timestamp_archivo': timestamp,
                    'fecha_procesamiento': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'actasContabilizadas': datos_raw.get('actasContabilizadas'),
                    'contabilizadas': datos_raw.get('contabilizadas'),
                    'totalActas': datos_raw.get('totalActas'),
                    'participacionCiudadana': datos_raw.get('participacionCiudadana'),
                    'totalVotosEmitidos': datos_raw.get('totalVotosEmitidos'),
                    'totalVotosValidos': datos_raw.get('totalVotosValidos'),
                    'archivo_origen': nombre_base
                }

    except Exception as e:
            print(f"⚠️ Error en archivo {file_path}: {e}")

    return fila

data_enriquecida = []
for file in json_files:
    full_path = os.path.join(CARPETA_PARAMETROS, file)
    if not os.path.exists(full_path):
        print(f"Archivo no encontrado: {file}")
        continue
    lecture = process_json_parametros(full_path)
    data_enriquecida.append(lecture)

# Aplanar la lista de listas
datos_planos = []
if isinstance(data_enriquecida, list) and len(data_enriquecida) > 0:
    if isinstance(data_enriquecida[0], list):
        datos_planos = [item for sublist in data_enriquecida for item in sublist]
    else:
        datos_planos = data_enriquecida
else:
    datos_planos = data_enriquecida

# Crear DataFrame
df_parametros = pd.DataFrame(datos_planos)
# Ver resultado
print(f"✅ DataFrame creado: {df_parametros.shape[0]} filas, {df_parametros.shape[1]} columnas")
print(df_parametros.head())
print(f"\n✅ Tabla creada: {df_parametros.shape[0]} filas, {df_parametros.shape[1]} columnas")
print(f"\n📊 Columnas disponibles:")
print(df_parametros.columns.tolist())

print("="*60)
print("FIN DE LA LECTURA - PARAMETROS")
print("="*60)

print("="*60)
print("INICIO DE LA LECTURA - GENERALES")
print("="*60)

try:
    json_files = os.listdir(CARPETA_PARAMETROS_GLOBALES)
except FileNotFoundError:
    print(f"Error: No se encontró la carpeta {CARPETA_PARAMETROS_GLOBALES}")

def process_json_parametros_globales(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        datos_raw = data['data']

        nombre_base = os.path.basename(file_path)
        nombre_sin_ext = nombre_base.replace('.json', '')
            
        # Extraer timestamp
        timestamp_match = re.search(r'_(\d{8}_\d{6})$', nombre_sin_ext)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        nombre_sin_timestamp = nombre_sin_ext[:timestamp_match.start()] if timestamp_match else nombre_sin_ext  

        fila = {
                    'fecha_procesamiento': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'actasContabilizadas': datos_raw.get('actasContabilizadas'),
                    'contabilizadas': datos_raw.get('contabilizadas'),
                    'totalActas': datos_raw.get('totalActas'),
                    'participacionCiudadana': datos_raw.get('participacionCiudadana'),
                    'totalVotosEmitidos': datos_raw.get('totalVotosEmitidos'),
                    'totalVotosValidos': datos_raw.get('totalVotosValidos'),
                    'archivo_origen': nombre_base
                }

    except Exception as e:
            print(f"⚠️ Error en archivo {file_path}: {e}")

    return fila

data_enriquecida = []
for file in json_files:
    full_path = os.path.join(CARPETA_PARAMETROS_GLOBALES, file)
    if not os.path.exists(full_path):
        print(f"Archivo no encontrado: {file}")
        continue
    lecture = process_json_parametros_globales(full_path)
    data_enriquecida.append(lecture)

# Aplanar la lista de listas
datos_planos = []
if isinstance(data_enriquecida, list) and len(data_enriquecida) > 0:
    if isinstance(data_enriquecida[0], list):
        datos_planos = [item for sublist in data_enriquecida for item in sublist]
    else:
        datos_planos = data_enriquecida
else:
    datos_planos = data_enriquecida

# Crear DataFrame
df_parametros_globales = pd.DataFrame(datos_planos)
# Ver resultado
print(f"✅ DataFrame creado: {df_parametros_globales.shape[0]} filas, {df_parametros_globales.shape[1]} columnas")
print(df_parametros_globales.head())
print(f"\n✅ Tabla creada: {df_parametros_globales.shape[0]} filas, {df_parametros_globales.shape[1]} columnas")
print(f"\n📊 Columnas disponibles:")
print(df_parametros_globales.columns.tolist())

print("="*60)
print("FIN DE LA LECTURA - GENERALES")
print("="*60)

# ============================================
# 3. FUNCIÓN DE PROYECCIÓN
# ============================================

# Convert timestamp to string and handle None values
df['timestamp_json'] = df['timestamp_json'].astype(str)
df = df[df['ubicacion'].notna()]

# Sort values - ensure timestamp is sortable
print("📊 DATOS DISPONIBLES PARA PROYECCIÓN")
print("=" * 70)
print(f"Total de registros: {len(df)}")
print(f"Ubigeos únicos: {df['ubicacion'].nunique()}")
print(f"Timestamps únicos: {df['timestamp_json'].nunique()}")

# Sort by ubicacion and timestamp
try:
    df = df.sort_values(['ubicacion', 'timestamp_json'])
    print("✅ DataFrame ordenado correctamente")
except Exception as e:
    print(f"⚠️ Error al ordenar: {e}")
    print("Continuando sin ordenar...")

def enriquecer_df(df, df_parametros, df_parametros_globales):
    # === 1. OBTENER EL ÚLTIMO REGISTRO POR UBIGEO ===
    df_ultimo = df.groupby(['ubicacion','nombre_candidato'], observed=True).last().reset_index()
    
    # Ensure ubicacion is string for merge
    df_parametros['ubicacion'] = df_parametros['ubicacion'].astype(str)
    df_ultimo['ubicacion'] = df_ultimo['ubicacion'].astype(str)
    
    par_ubigeo = df_parametros[['ubicacion', 'actasContabilizadas', 'contabilizadas', 'totalActas', 
                                'participacionCiudadana','totalVotosEmitidos','totalVotosValidos']].set_index('ubicacion').add_suffix('_ubigeo')
    
    df_ultimo = df_ultimo.merge(par_ubigeo, left_on='ubicacion', right_index=True, how='left')
    
    par_global = df_parametros_globales[['actasContabilizadas', 'contabilizadas','totalActas',  
                                        'participacionCiudadana','totalVotosEmitidos','totalVotosValidos']].add_suffix('_global')
    
    # Cross join - handle empty dataframes
    if len(par_global) > 0:
        df_ultimo = df_ultimo.merge(par_global, how='cross')
    else:
        # Add empty columns if no global data
        for col in par_global.columns:
            df_ultimo[col] = None
    
    return df_ultimo

df_enriquecido = enriquecer_df(df, df_parametros, df_parametros_globales)
print(f"✅ DataFrame enriquecido: {len(df_enriquecido)} filas")


## Guardar el df_enriquecido para implementar modelo matematico

if not df_enriquecido.empty:
    evo_nac = df_enriquecido.sort_values('timestamp_json', ascending=False)
    print("\n" + "="*60)
    print("Data Global")
    print("="*60)
    print(df_enriquecido.to_string())
    
    # Crear carpeta si no existe
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    
    # Guardar en la carpeta
    ruta_completa = os.path.join(CARPETA_SALIDA, 'evolucion_eleccion.csv')
    evo_nac.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
    print(f"\n✅ Archivo guardado en: {ruta_completa}")
else:
    print("❌ No se pudo generar la evolucion nacional")


######

def proyectar_votos(df_ubigeo, candidato):
    df_cand = df_ubigeo[df_ubigeo['nombre_agrupacion'] == candidato].copy()
    if len(df_cand) == 0:
        return None
    
    df_cand = df_cand.sort_values('timestamp_json')
    ultimo = df_cand.iloc[-1]
    
    # Datos candidato
    votos_actuales = ultimo['total_votos_validos']
    intencion_voto = ultimo['porcentaje_votos_emitidos']
    
    # Datos ubigeo
    porcentaje_actas_ubigeo = ultimo.get('actasContabilizadas_ubigeo', 0)
    actasContabilizadas_ubigeo = ultimo.get('contabilizadas_ubigeo', 0)
    totalVotosEmitidos_ubigeo = ultimo.get('totalVotosEmitidos_ubigeo', 0)
    totalActas_ubigeo = ultimo.get('totalActas_ubigeo', 0)
    participacionCiudadana_ubigeo = ultimo.get('participacionCiudadana_ubigeo', 0)
    
    # Datos Totales
    actasContabilizadas_global = ultimo.get('actasContabilizadas_global', 0)
    contabilizadas_global = ultimo.get('contabilizadas_global', 0)
    totalActas_global = ultimo.get('totalActas_global', 0)
    participacionCiudadana_global = ultimo.get('participacionCiudadana_global', 0)
    totalVotosEmitidos_global = ultimo.get('totalVotosEmitidos_global', 0)
    
    if votos_actuales == 0 or actasContabilizadas_ubigeo == 0:
        return None
    
    try:
        votos_total = int((totalVotosEmitidos_ubigeo * totalActas_ubigeo) / actasContabilizadas_ubigeo)
        votos_total_faltantes = votos_total - totalVotosEmitidos_ubigeo
        votos_proyectados_lineal = votos_actuales + int(votos_total_faltantes * (intencion_voto / 100) * (participacionCiudadana_ubigeo / 100))
        incremento = votos_proyectados_lineal - votos_actuales
        
        return {
            'candidato': candidato,
            'ubicacion': ultimo['ubicacion'],
            'votos_actuales': int(votos_actuales),
            'intencion_actual': float(intencion_voto / 100),
            'votos_proyectados': votos_proyectados_lineal,
            'incremento': incremento
        }
    except Exception as e:
        print(f"⚠️ Error proyectando {candidato} en {ultimo['ubicacion']}: {e}")
        return None

def proyectar_todos(df):
    proyecciones = []
    
    if df.empty:
        print("⚠️ DataFrame vacío, no se pueden calcular proyecciones")
        return pd.DataFrame()
    
    # Verificar columnas necesarias
    if 'nombre_agrupacion' not in df.columns:
        print("❌ Columna 'nombre_agrupacion' no encontrada")
        return pd.DataFrame()
    
    # Filter out BLANCO and NULO
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

df_proyectado = proyectar_todos(df_enriquecido)
print(f"✅ Proyecciones calculadas: {len(df_proyectado)} filas")

def proyeccion_nacional_lineal(df):
    df = df.copy()
    proy_nac = []  # Lista vacía
    
    # Manejar caso de DataFrame vacío
    if df.empty:
        print("⚠️ DataFrame de proyecciones vacío")
        return pd.DataFrame()
    
    candidatos = df['candidato'].unique()
    votos_total = df['votos_actuales'].sum()
    votos_proy = df['votos_proyectados'].sum()
    
    # Evitar división por cero
    if votos_total == 0 or votos_proy == 0:
        print("⚠️ Advertencia: Total de votos es 0")
        return pd.DataFrame()
    
    for cand in candidatos:
        df_cand = df[df['candidato'] == cand]
        votos_actuales = df_cand['votos_actuales'].sum()
        intencion_nacional = ((votos_actuales / votos_total) * 100).round(2)
        votos_proyectados = df_cand['votos_proyectados'].sum()
        incremento = votos_proyectados - votos_actuales
        intencion_proyectada = ((votos_proyectados / votos_proy) * 100).round(2)
        
        datos = {
            'candidato': cand,
            'votos_actuales': votos_actuales,
            'intencion_nacional': intencion_nacional,
            'votos_proyectados': votos_proyectados,
            'incremento': incremento,
            'intencion_proyectada': intencion_proyectada
        }
        proy_nac.append(datos)
    
    return pd.DataFrame(proy_nac)

proy_nac = proyeccion_nacional_lineal(df_proyectado)

if not proy_nac.empty:
    proy_nac = proy_nac.sort_values('votos_proyectados', ascending=False)
    print("\n" + "="*60)
    print("PROYECCIÓN NACIONAL")
    print("="*60)
    print(proy_nac.to_string())
    
    # Crear carpeta si no existe
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    
    # Guardar en la carpeta
    ruta_completa = os.path.join(CARPETA_SALIDA, 'proyeccion_nacional.csv')
    proy_nac.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
    print(f"\n✅ Archivo guardado en: {ruta_completa}")
else:
    print("❌ No se pudo generar la proyección nacional")