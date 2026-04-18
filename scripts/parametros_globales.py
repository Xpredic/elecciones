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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = 'C:/Users/gamar/Documents/proyectos-git/git-elecciones'
DATA_DIR = os.path.join(BASE_DIR, "data")

CARPETA_JSON = os.path.join(DATA_DIR, "json")
CARPETA_PARAMETROS = os.path.join(DATA_DIR, "parametros")
CARPETA_PARAMETROS_GLOBALES = os.path.join(DATA_DIR, "parametros_globales")
CARPETA_SALIDA = os.path.join(DATA_DIR, "tablas")

# === CREAR CARPETA DATA/JSON SI NO EXISTE ===
os.makedirs("../data/data/parametros_globales", exist_ok=True)

# === INICIO DEL TIMER ===
tiempo_inicio = time.time()
inicio_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Para nombres de archivo

def obtener_datos_con_selenium(nombre=None):
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
        url = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/resumen-general/totales?idEleccion=10&tipoFiltro=eleccion"
        
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
            nombre_archivo = nombre_archivo = f"{CARPETA_PARAMETROS_GLOBALES}/parametros_globales.json"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ Parámetros globales guardados → {nombre_archivo}")
            driver.quit()
            return True
        else:
            print(f"❌ Parámetros globales: No es JSON - {page_text[:100]}")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Parámetros globales: Error - {e}")
        try:
            driver.quit()
        except:
            pass
        return False

# === EJECUTAR ===
print("=" * 60)
print("📊 OBTENIENDO PARÁMETROS GLOBALES")
print("=" * 60)
print(f"Timestamp: {timestamp}")
print("-" * 60)


obtener_datos_con_selenium()
time.sleep(0.5)  # Pequeña pausa para no sobrecargar el servidor

print("\n" + "=" * 60)
print("✅ PROCESO COMPLETADO")
print("=" * 60)