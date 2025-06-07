from flask import Flask, render_template
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Ruta fija del Excel
EXCEL_PATH = "datos/trabajos.xlsx"
IMAGES_PATH = "static/imagenes"

# Lista de zonas disponibles
ZONAS_DISPONIBLES = ['africa', 'asia', 'churute', 'korea']

# Leer el archivo de datos
def leer_datos():
    try:
        if not os.path.exists(EXCEL_PATH):
            print(f"ERROR: No se encuentra el archivo {EXCEL_PATH}")
            return pd.DataFrame()
        
        df = pd.read_excel(EXCEL_PATH)
        print("Columnas detectadas:", df.columns.tolist())
        
        # Verificar que existan las columnas necesarias
        columnas_requeridas = ["Zona", "Trabajo", "Tipo", "Fecha", "Días", "Avance"]
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            print(f"ADVERTENCIA: Columnas faltantes: {columnas_faltantes}")
        
        # Limpiar la columna Zona si existe
        if "Zona" in df.columns:
            df["Zona"] = df["Zona"].astype(str).str.strip().str.lower()
        
        # Manejar valores nulos en fechas
        if "Fecha" in df.columns:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
        
        # Convertir la columna Avance a numérico
        if "Avance" in df.columns:
            df["Avance"] = pd.to_numeric(df["Avance"], errors='coerce').fillna(0).astype(int)
        
        # Convertir la columna Días a numérico si existe
        if "Días" in df.columns:
            df["Días"] = pd.to_numeric(df["Días"], errors='coerce').fillna(0).astype(int)
        
        return df
        
    except Exception as e:
        print(f"ERROR al leer datos: {e}")
        return pd.DataFrame()

# Obtener imágenes por zona
def obtener_imagenes_por_zona(zona):
    try:
        carpeta = os.path.join(IMAGES_PATH, zona.lower())
        if not os.path.exists(carpeta):
            print(f"Carpeta no existe: {carpeta}")
            return []
        
        imagenes = []
        extensiones_validas = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
        
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(extensiones_validas):
                ruta_imagen = f"/static/imagenes/{zona.lower()}/{archivo}"
                imagenes.append(ruta_imagen)
        
        return sorted(imagenes)
    
    except Exception as e:
        print(f"ERROR al obtener imágenes: {e}")
        return []

# Obtener siguiente zona
def obtener_siguiente_zona(zona_actual):
    try:
        zona_actual = zona_actual.lower()
        if zona_actual in ZONAS_DISPONIBLES:
            indice_actual = ZONAS_DISPONIBLES.index(zona_actual)
            siguiente_indice = (indice_actual + 1) % len(ZONAS_DISPONIBLES)
            return ZONAS_DISPONIBLES[siguiente_indice]
        else:
            return ZONAS_DISPONIBLES[0]
    except:
        return ZONAS_DISPONIBLES[0]

# Obtener zona anterior
def obtener_zona_anterior(zona_actual):
    try:
        zona_actual = zona_actual.lower()
        if zona_actual in ZONAS_DISPONIBLES:
            indice_actual = ZONAS_DISPONIBLES.index(zona_actual)
            anterior_indice = (indice_actual - 1) % len(ZONAS_DISPONIBLES)
            return ZONAS_DISPONIBLES[anterior_indice]
        else:
            return ZONAS_DISPONIBLES[-1]
    except:
        return ZONAS_DISPONIBLES[-1]

@app.route('/')
def portada():
    try:
        semana = datetime.today().isocalendar().week
        
        # Obtener zonas disponibles del archivo Excel
        df = leer_datos()
        if not df.empty and "Zona" in df.columns:
            zonas_excel = sorted(df["Zona"].dropna().unique())
            # Combinar zonas del Excel con las predeterminadas
            zonas_disponibles = list(set(ZONAS_DISPONIBLES + zonas_excel))
            zonas_disponibles.sort()
        else:
            zonas_disponibles = ZONAS_DISPONIBLES
        
        return render_template("index.html", 
                             semana=semana - 1,  
                             zonas_disponibles=zonas_disponibles)
    
    except Exception as e:
        print(f"ERROR en portada: {e}")
        return f"<h1>Error al cargar la página principal</h1><p>{str(e)}</p>"

@app.route('/zona/<nombre_zona>')
def mostrar_zona(nombre_zona):
    try:
        df = leer_datos()
        trabajos = []
        
        if not df.empty:
            # Filtrar trabajos por zona (case-insensitive)
            zona_filtrada = df[df["Zona"] == nombre_zona.lower()]
            trabajos = zona_filtrada.to_dict(orient="records")
            
            # Asegurar que todos los valores numéricos estén correctos
            for trabajo in trabajos:
                # Convertir Avance a entero seguro
                if 'Avance' in trabajo:
                    try:
                        trabajo['Avance'] = int(float(str(trabajo['Avance']).replace('%', '').replace(',', '.')))
                    except (ValueError, TypeError):
                        trabajo['Avance'] = 0
                
                # Convertir Días a entero seguro
                if 'Días' in trabajo:
                    try:
                        trabajo['Días'] = int(float(str(trabajo['Días'])))
                    except (ValueError, TypeError):
                        trabajo['Días'] = 0
        
        imagenes = obtener_imagenes_por_zona(nombre_zona)
        siguiente_zona = obtener_siguiente_zona(nombre_zona)
        zona_anterior = obtener_zona_anterior(nombre_zona)
        
        return render_template("zona.html", 
                             zona=nombre_zona, 
                             trabajos=trabajos, 
                             imagenes=imagenes,
                             siguiente_zona=siguiente_zona,
                             zona_anterior=zona_anterior,
                             zonas_disponibles=ZONAS_DISPONIBLES)
    
    except Exception as e:
        print(f"ERROR en zona {nombre_zona}: {e}")
        return f"<h1>Error al cargar la zona {nombre_zona}</h1><p>{str(e)}</p>"

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def error_servidor(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    # Verificar que existan las carpetas necesarias
    carpetas_necesarias = [
        "datos",
        "static/imagenes",
        "static/css",
        "templates"
    ]
    
    for carpeta in carpetas_necesarias:
        if not os.path.exists(carpeta):
            print(f"ADVERTENCIA: La carpeta '{carpeta}' no existe, creándola...")
            os.makedirs(carpeta, exist_ok=True)
    
    # Crear subcarpetas para cada zona
    for zona in ZONAS_DISPONIBLES:
        zona_path = os.path.join("static/imagenes", zona)
        if not os.path.exists(zona_path):
            print(f"Creando carpeta para zona: {zona}")
            os.makedirs(zona_path, exist_ok=True)
    
    print("Iniciando servidor Flask...")
    print(f"Zonas disponibles: {ZONAS_DISPONIBLES}")
    app.run(debug=True, host='0.0.0.0', port=5000)