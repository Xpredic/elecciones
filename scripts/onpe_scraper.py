import json
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# === CREAR CARPETA DATA/JSON SI NO EXISTE ===
os.makedirs("../data/json", exist_ok=True)

# === INICIO DEL TIMER ===
tiempo_inicio = time.time()
inicio_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("=" * 60)
print(f"🚀 INICIANDO EXTRACCIÓN JSON - {inicio_str}")
print(f"📁 Timestamp: {timestamp}")
print("=" * 60)

# === DEFINIR UBIGEOS POR ÁMBITO ===
ubigeos_ambito1 = [
    '010000', '020000', '030000', '040000', '050000', 
    '060000', '070000', '080000', '090000', '100000', 
    '110000', '120000', '130000', '140000', '150000', 
    '160000', '170000', '180000', '190000', '200000', 
    '210000', '220000', '230000', '240000', '250000'
]

ubigeos_ambito2 = [
    '910000', '920000', '930000', '940000', '950000'
]

nombres_ambito2 = {
    '910000': 'region_91',
    '920000': 'region_92',
    '930000': 'region_93',
    '940000': 'region_94',
    '950000': 'region_95'
}

# Contadores
exitos = 0
fallos = 0

# CARPETAS BASE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = 'C:/Users/gamar/Documents/proyectos-git/git-elecciones'
DATA_DIR = os.path.join(BASE_DIR, "data")

CARPETA_JSON = os.path.join(DATA_DIR, "json")
CARPETA_PARAMETROS = os.path.join(DATA_DIR, "parametros")
CARPETA_PARAMETROS_GLOBALES = os.path.join(DATA_DIR, "parametros_globales")
CARPETA_SALIDA = os.path.join(DATA_DIR, "tablas")

# Crear directorio
os.makedirs("../data/json", exist_ok=True)

def obtener_datos_con_selenium(ambito, ubigeo, nombre=None):
    """
    Obtiene datos usando Selenium (navegador real)
    """
    global exitos, fallos
    
    # Configurar opciones
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Para ejecutar en segundo plano (sin ventana visible)
    # options.add_argument("--headless")
    
    try:
        # Iniciar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Construir URL
        url = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/eleccion-presidencial/participantes-ubicacion-geografica-nombre?tipoFiltro=ubigeo_nivel_01&idAmbitoGeografico={ambito}&ubigeoNivel1={ubigeo}&idEleccion=10"
        
        print(f"🌐 Accediendo a: {url[:80]}...")
        driver.get(url)
        
        # Esperar que cargue el JSON (la página muestra el JSON directamente)
        time.sleep(3)
        
        # Obtener el texto de la página (que debería ser JSON)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Verificar si es JSON válido
        if page_text.startswith('{'):
            data = json.loads(page_text)
            
            # Guardar archivo
            nombre_archivo = f"{CARPETA_JSON}/resultados_ambito{ambito}_{ubigeo}_{timestamp}.json"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            participantes = len(data.get('data', []))
            print(f"✅ {ubigeo}: {participantes} participantes")
            driver.quit()
            return True
        else:
            print(f"❌ {ubigeo}: No es JSON - {page_text[:100]}")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ {ubigeo}: Error - {e}")
        try:
            driver.quit()
        except:
            pass
        return False

# Ejecutar
print("=" * 60)
print("📊 PROCESANDO PARÁMETROS CON SELENIUM")
print("=" * 60)

print("\n📊 PROCESANDO ÁMBITO 1 - DEPARTAMENTOS (25)")
print("-" * 40)

# Contadores
exitos = 0
fallos = 0
for i, ubigeo in enumerate(ubigeos_ambito1, 1):
    print(f"[{i:2}/25] Procesando {ubigeo}...")
    if obtener_datos_con_selenium(ambito=1, ubigeo=ubigeo):
        exitos += 1
    time.sleep(1)  # Pausa entre peticiones

print("\n" + "=" * 60)
print(f"✅ COMPLETADO: {exitos}/25 exitosos")
print("=" * 60)

# === EJECUTAR PARA ÁMBITO 2 ===
print("\n📊 PROCESANDO ÁMBITO 2 - REGIONES ESPECIALES (5)")
print("-" * 40)

# Contadores
exitos = 0
fallos = 0
for i, ubigeo in enumerate(ubigeos_ambito2, 1):
    print(f"[{i:2}/5] Procesando {ubigeo}...")
    if obtener_datos_con_selenium(ambito=2, ubigeo=ubigeo):
        exitos += 1
    time.sleep(1)  # Pausa entre peticiones

print("\n" + "=" * 60)
print(f"✅ COMPLETADO: {exitos}/5 exitosos")
print("=" * 60)


# === RESUMEN FINAL ===
tiempo_total = time.time() - tiempo_inicio
fin_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("\n" + "=" * 60)
print("📊 RESUMEN DE EJECUCIÓN")
print("=" * 60)
print(f"🕐 Inicio:     {inicio_str}")
print(f"🕐 Fin:        {fin_str}")
print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
print(f"✅ Exitosos:   {exitos}")
print(f"❌ Fallidos:   {fallos}")
print(f"📁 Archivos en: data/json/")
print("=" * 60)