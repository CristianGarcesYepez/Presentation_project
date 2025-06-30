from flask import Flask, render_template, url_for
import pandas as pd
import os
from datetime import datetime
from agenda_app import init_agenda_routes

app = Flask(__name__)
# Inicializar rutas de agenda
init_agenda_routes(app)

# Ruta fija del Excel
EXCEL_PATH = "datos/trabajos.xlsx"
IMAGES_PATH = "static/imagenes"

MEGAZONAS_list = ['Media', 'California', 'Taura', 'Peninsula', 'Oceanía', 'Golfo']

MEGAZONAS = {
    'Media': ['Bajen A','Bajen B','Corvinero A','Corvinero B','Daular','Africa','Asia'],
    'California': ['California', 'Churute'],
    'Taura': ['Taura A', 'Taura B', 'Taura C', 'Taura D'],
    'Peninsula': ['Chanduy', 'Pañamao'],
    'Oceanía': ['Korea', 'Playas', 'Sabana'],
    'Golfo': ['Golfo']
}
# Lista de zonas disponibles - construida dinámicamente desde MEGAZONAS
ZONAS_DISPONIBLES = []
for zonas in MEGAZONAS.values():
    ZONAS_DISPONIBLES.extend([zona.lower() for zona in zonas])
ZONAS_DISPONIBLES = list(set(ZONAS_DISPONIBLES))  # Eliminar duplicados

print(f"Zonas disponibles desde MEGAZONAS: {ZONAS_DISPONIBLES}")

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
            # Filtrar filas with zona válida (no NaN, no vacías)
            df = df[df["Zona"].notna() & (df["Zona"] != '') & (df["Zona"] != 'nan')]
        
        # Manejar valores nulos en fechas
        if "Fecha" in df.columns:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
        
        # Convertir la columna Avance a numérico
        if "Avance" in df.columns:
            df["Avance"] = pd.to_numeric(df["Avance"], errors='coerce').fillna(0)
            # Asegurar que esté entre 0 y 100
            df["Avance"] = df["Avance"].clip(0, 100).round().astype(int)
        
        # Convertir la columna Días a numérico si existe
        if "Días" in df.columns:
            df["Días"] = pd.to_numeric(df["Días"], errors='coerce').fillna(0).astype(int)
        
        return df
        
    except FileNotFoundError:
        print(f"ERROR: No se puede encontrar el archivo {EXCEL_PATH}")
        return pd.DataFrame()
    except PermissionError:
        print(f"ERROR: No se tienen permisos para leer {EXCEL_PATH}")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERROR al leer datos: {e}")
        return pd.DataFrame()

# Obtener imágenes por zona - CORREGIDO
def obtener_imagenes_por_zona(zona):
    try:
        carpeta = os.path.join(IMAGES_PATH, zona.lower())
        print(f"Buscando imágenes en: {carpeta}")
        
        if not os.path.exists(carpeta):
            print(f"Carpeta no existe: {carpeta}")
            return []
        
        imagenes = []
        extensiones_validas = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
        
        archivos = os.listdir(carpeta)
        print(f"Archivos encontrados en {carpeta}: {archivos}")
        
        for archivo in archivos:
            if archivo.lower().endswith(extensiones_validas):
                # Usar url_for para generar las rutas correctas
                ruta_imagen = url_for('static', filename=f'imagenes/{zona.lower()}/{archivo}')
                imagenes.append(ruta_imagen)
                print(f"Imagen agregada: {ruta_imagen}")
        
        print(f"Total imágenes encontradas para {zona}: {len(imagenes)}")
        return sorted(imagenes)
    
    except PermissionError:
        print(f"ERROR: Sin permisos para acceder a la carpeta {carpeta}")
        return []
    except Exception as e:
        print(f"ERROR al obtener imágenes para {zona}: {e}")
        return []

# Obtener siguiente zona
def obtener_siguiente_zona(zona_actual):
    try:
        zona_actual = zona_actual.lower().strip()
        if zona_actual in ZONAS_DISPONIBLES:
            indice_actual = ZONAS_DISPONIBLES.index(zona_actual)
            siguiente_indice = (indice_actual + 1) % len(ZONAS_DISPONIBLES)
            return ZONAS_DISPONIBLES[siguiente_indice]
        else:
            return ZONAS_DISPONIBLES[0] if ZONAS_DISPONIBLES else None
    except Exception as e:
        print(f"ERROR al obtener siguiente zona: {e}")
        return ZONAS_DISPONIBLES[0] if ZONAS_DISPONIBLES else None

# Obtener zona anterior
def obtener_zona_anterior(zona_actual):
    try:
        zona_actual = zona_actual.lower().strip()
        if zona_actual in ZONAS_DISPONIBLES:
            indice_actual = ZONAS_DISPONIBLES.index(zona_actual)
            anterior_indice = (indice_actual - 1) % len(ZONAS_DISPONIBLES)
            return ZONAS_DISPONIBLES[anterior_indice]
        else:
            return ZONAS_DISPONIBLES[-1] if ZONAS_DISPONIBLES else None
    except Exception as e:
        print(f"ERROR al obtener zona anterior: {e}")
        return ZONAS_DISPONIBLES[-1] if ZONAS_DISPONIBLES else None

@app.route('/')
def portada():
    try:
        semana = datetime.now().isocalendar()[1]  # Método más compatible
        
        # Obtener zonas disponibles del archivo Excel
        df = leer_datos()
        zonas_disponibles = ZONAS_DISPONIBLES.copy()  # Copia para evitar modificar la original
        
        if not df.empty and "Zona" in df.columns:
            zonas_excel = df["Zona"].dropna().unique().tolist()
            zonas_excel = [zona for zona in zonas_excel if zona and str(zona).strip()]
            
            # Combinar zonas del Excel con las predeterminadas (sin duplicados)
            zonas_combinadas = list(set(zonas_disponibles + zonas_excel))
            zonas_disponibles = sorted(zonas_combinadas)
        
        return render_template("index.html", 
                             semana=semana,  
                             zonas_disponibles=zonas_disponibles)
    
    except Exception as e:
        print(f"ERROR en portada: {e}")
        try:
            return render_template("error.html", 
                                 mensaje="Error al cargar la página principal",
                                 detalle=str(e)), 500
        except:
            return f"<h1>Error al cargar la página principal</h1><p>{str(e)}</p>", 500

@app.route('/zona/<nombre_zona>')
def mostrar_zona(nombre_zona):
    try:
        print(f"Mostrando zona: {nombre_zona}")
        
        # Validar que la zona existe
        if nombre_zona.lower() not in [zona.lower() for zona in ZONAS_DISPONIBLES]:
            try:
                return render_template("error.html", 
                                    mensaje=f"Zona '{nombre_zona}' no encontrada",
                                    detalle="Las zonas disponibles son: " + ", ".join(ZONAS_DISPONIBLES)), 404
            except:
                return f"<h1>Zona '{nombre_zona}' no encontrada</h1><p>Zonas disponibles: {', '.join(ZONAS_DISPONIBLES)}</p>", 404
        
        df = leer_datos()
        trabajos = []
        
        if not df.empty and "Zona" in df.columns:
            # Filtrar trabajos por zona (case-insensitive)
            zona_filtrada = df[df["Zona"].str.lower() == nombre_zona.lower()]
            
            if not zona_filtrada.empty:
                trabajos = zona_filtrada.to_dict(orient="records")
                
                # Procesar cada trabajo para asegurar tipos correctos
                for trabajo in trabajos:
                    # Procesar Avance
                    if 'Avance' in trabajo:
                        try:
                            avance_val = trabajo['Avance']
                            if pd.isna(avance_val):
                                trabajo['Avance'] = 0
                            else:
                                # Convertir string a número si es necesario
                                if isinstance(avance_val, str):
                                    avance_val = avance_val.replace('%', '').replace(',', '.').strip()
                                trabajo['Avance'] = max(0, min(100, int(float(avance_val))))
                        except (ValueError, TypeError):
                            trabajo['Avance'] = 0
                    
                    # Procesar Días
                    if 'Días' in trabajo:
                        try:
                            dias_val = trabajo['Días']
                            if pd.isna(dias_val):
                                trabajo['Días'] = 0
                            else:
                                trabajo['Días'] = int(float(dias_val))
                        except (ValueError, TypeError):
                            trabajo['Días'] = 0
        
        # Obtener imágenes - MEJORADO con más debugging
        imagenes = obtener_imagenes_por_zona(nombre_zona)
        print(f"Imágenes obtenidas para {nombre_zona}: {imagenes}")
        
        siguiente_zona = obtener_siguiente_zona(nombre_zona)
        zona_anterior = obtener_zona_anterior(nombre_zona)
        
        # Obtener la Megazona a la que pertenece esta zona
        megazona_actual = obtener_megazona_de_zona(nombre_zona)
        
        # Obtener zonas de la Megazona actual con datos
        zonas_megazona = []
        zonas_megazona_con_datos = []
        
        if megazona_actual and megazona_actual in MEGAZONAS:
            zonas_megazona = MEGAZONAS[megazona_actual]
            
            # Verificar cuáles zonas de esta Megazona tienen datos
            if not df.empty and "Zona" in df.columns:
                zonas_excel = df["Zona"].dropna().unique().tolist()
                zonas_excel = [zona.lower().strip() for zona in zonas_excel if zona and str(zona).strip()]
                
                for zona in zonas_megazona:
                    if zona.lower().strip() in zonas_excel:
                        zonas_megazona_con_datos.append(zona)
        
        # Calcular siguiente zona dentro de la Megazona
        siguiente_zona_megazona = None
        if zonas_megazona_con_datos:
            try:
                # Buscar la zona actual en la lista de zonas con datos de la Megazona
                zonas_lower = [z.lower() for z in zonas_megazona_con_datos]
                if nombre_zona.lower() in zonas_lower:
                    current_index = zonas_lower.index(nombre_zona.lower())
                    next_index = (current_index + 1) % len(zonas_megazona_con_datos)
                    siguiente_zona_megazona = zonas_megazona_con_datos[next_index]
                else:
                    # Si la zona actual no tiene datos, usar la primera zona con datos
                    siguiente_zona_megazona = zonas_megazona_con_datos[0]
            except (ValueError, IndexError):
                siguiente_zona_megazona = None
        
        return render_template("zona.html", 
                             zona=nombre_zona.title(), 
                             trabajos=trabajos, 
                             imagenes=imagenes,
                             siguiente_zona=siguiente_zona,
                             zona_anterior=zona_anterior,
                             zonas_disponibles=ZONAS_DISPONIBLES,
                             megazona_actual=megazona_actual,
                             zonas_megazona=zonas_megazona,
                             zonas_megazona_con_datos=zonas_megazona_con_datos,
                             siguiente_zona_megazona=siguiente_zona_megazona)
    
    except Exception as e:
        print(f"ERROR en zona {nombre_zona}: {e}")
        try:
            return render_template("error.html", 
                                 mensaje=f"Error al cargar la zona {nombre_zona}",
                                 detalle=str(e)), 500
        except:
            return f"<h1>Error al cargar la zona {nombre_zona}</h1><p>{str(e)}</p>", 500

@app.route('/menu')
def menu():
    try:
        semana = datetime.now().isocalendar()[1]  # Método más compatible
        
        # Obtener datos del Excel para determinar qué zonas tienen datos
        df = leer_datos()
        zonas_con_datos = []
        
        if not df.empty and "Zona" in df.columns:
            zonas_con_datos = df["Zona"].dropna().unique().tolist()
            zonas_con_datos = [zona.lower().strip() for zona in zonas_con_datos if zona and str(zona).strip()]
        
        # Procesar Megazonas y determinar cuáles tienen datos disponibles
        megazonas_info = {}
        for megazona, zonas in MEGAZONAS.items():
            zonas_disponibles = []
            zonas_sin_datos = []
            
            for zona in zonas:
                zona_lower = zona.lower().strip()
                if zona_lower in zonas_con_datos:
                    zonas_disponibles.append(zona)
                else:
                    zonas_sin_datos.append(zona)
            
            megazonas_info[megazona] = {
                'zonas_disponibles': zonas_disponibles,
                'zonas_sin_datos': zonas_sin_datos,
                'total_zonas': len(zonas),
                'tiene_datos': len(zonas_disponibles) > 0,
                'zona_principal': zonas_disponibles[0] if zonas_disponibles else zonas[0]  # Primera zona con datos o primera zona
            }
        
        return render_template("menu.html", 
                             semana=semana,
                             megazonas=megazonas_info,
                             megazonas_list=MEGAZONAS_list)
    except Exception as e:
        print(f"ERROR en menú: {e}")
        try:
            return render_template("error.html", 
                                 mensaje="Error al cargar el menú",
                                 detalle=str(e)), 500
        except:
            return f"<h1>Error al cargar el menú</h1><p>{str(e)}</p>", 500

@app.route('/megazona/<nombre_megazona>')
def mostrar_megazona(nombre_megazona):
    try:
        print(f"Mostrando megazona: {nombre_megazona}")
        
        # Validar que la megazona existe
        if nombre_megazona not in MEGAZONAS:
            try:
                return render_template("error.html", 
                                    mensaje=f"Megazona '{nombre_megazona}' no encontrada",
                                    detalle="Las megazonas disponibles son: " + ", ".join(MEGAZONAS_list)), 404
            except:
                return f"<h1>Megazona '{nombre_megazona}' no encontrada</h1><p>Megazonas disponibles: {', '.join(MEGAZONAS_list)}</p>", 404
        
        df = leer_datos()
        zonas_megazona = MEGAZONAS[nombre_megazona]
        trabajos_por_zona = {}
        total_trabajos = []
        
        if not df.empty and "Zona" in df.columns:
            for zona in zonas_megazona:
                # Filtrar trabajos por zona (case-insensitive)
                zona_filtrada = df[df["Zona"].str.lower() == zona.lower()]
                
                if not zona_filtrada.empty:
                    trabajos_zona = zona_filtrada.to_dict(orient="records")
                    
                    # Procesar cada trabajo para asegurar tipos correctos
                    for trabajo in trabajos_zona:
                        # Procesar Avance
                        if 'Avance' in trabajo:
                            try:
                                avance_val = trabajo['Avance']
                                if pd.isna(avance_val):
                                    trabajo['Avance'] = 0
                                else:
                                    if isinstance(avance_val, str):
                                        avance_val = avance_val.replace('%', '').replace(',', '.').strip()
                                    trabajo['Avance'] = max(0, min(100, int(float(avance_val))))
                            except (ValueError, TypeError):
                                trabajo['Avance'] = 0
                        
                        # Procesar Días
                        if 'Días' in trabajo:
                            try:
                                dias_val = trabajo['Días']
                                if pd.isna(dias_val):
                                    trabajo['Días'] = 0
                                else:
                                    trabajo['Días'] = int(float(dias_val))
                            except (ValueError, TypeError):
                                trabajo['Días'] = 0
                    
                    trabajos_por_zona[zona] = trabajos_zona
                    total_trabajos.extend(trabajos_zona)
                else:
                    trabajos_por_zona[zona] = []
        
        # Obtener imágenes de la primera zona con datos o la primera zona
        zona_principal = None
        for zona in zonas_megazona:
            if zona.lower() in [z.lower() for z in trabajos_por_zona.keys() if trabajos_por_zona[z]]:
                zona_principal = zona
                break
        
        if not zona_principal:
            zona_principal = zonas_megazona[0] if zonas_megazona else 'default'
        
        imagenes = obtener_imagenes_por_zona(zona_principal)
        
        # Navegación entre megazonas
        siguiente_megazona = obtener_siguiente_megazona(nombre_megazona)
        megazona_anterior = obtener_megazona_anterior(nombre_megazona)
        
        return render_template("megazona.html", 
                             megazona=nombre_megazona,
                             zonas_megazona=zonas_megazona,
                             trabajos_por_zona=trabajos_por_zona,
                             total_trabajos=total_trabajos,
                             imagenes=imagenes,
                             siguiente_megazona=siguiente_megazona,
                             megazona_anterior=megazona_anterior,
                             megazonas_disponibles=MEGAZONAS_list)
    
    except Exception as e:
        print(f"ERROR en megazona {nombre_megazona}: {e}")
        try:
            return render_template("error.html", 
                                 mensaje=f"Error al cargar la megazona {nombre_megazona}",
                                 detalle=str(e)), 500
        except:
            return f"<h1>Error al cargar la megazona {nombre_megazona}</h1><p>{str(e)}</p>", 500

# Funciones auxiliares para navegación de megazonas
def obtener_siguiente_megazona(megazona_actual):
    try:
        if megazona_actual in MEGAZONAS_list:
            indice_actual = MEGAZONAS_list.index(megazona_actual)
            siguiente_indice = (indice_actual + 1) % len(MEGAZONAS_list)
            return MEGAZONAS_list[siguiente_indice]
        else:
            return MEGAZONAS_list[0] if MEGAZONAS_list else None
    except Exception as e:
        print(f"ERROR al obtener siguiente megazona: {e}")
        return MEGAZONAS_list[0] if MEGAZONAS_list else None

def obtener_megazona_anterior(megazona_actual):
    try:
        if megazona_actual in MEGAZONAS_list:
            indice_actual = MEGAZONAS_list.index(megazona_actual)
            anterior_indice = (indice_actual - 1) % len(MEGAZONAS_list)
            return MEGAZONAS_list[anterior_indice]
        else:
            return MEGAZONAS_list[-1] if MEGAZONAS_list else None
    except Exception as e:
        print(f"ERROR al obtener megazona anterior: {e}")
        return MEGAZONAS_list[-1] if MEGAZONAS_list else None

# Obtener la Megazona a la que pertenece una zona específica
def obtener_megazona_de_zona(nombre_zona):
    try:
        nombre_zona_lower = nombre_zona.lower().strip()
        for megazona, zonas in MEGAZONAS.items():
            for zona in zonas:
                if zona.lower().strip() == nombre_zona_lower:
                    return megazona
        return None
    except Exception as e:
        print(f"ERROR al obtener megazona de zona {nombre_zona}: {e}")
        return None

@app.errorhandler(404)
def pagina_no_encontrada(e):
    try:
        return render_template("error.html", 
                             mensaje="Página no encontrada",
                             detalle="La página que buscas no existe"), 404
    except:
        return "<h1>404 - Página no encontrada</h1><p>La página que buscas no existe</p>", 404

@app.errorhandler(500)
def error_servidor(e):
    try:
        return render_template("error.html", 
                             mensaje="Error interno del servidor",
                             detalle="Ha ocurrido un error inesperado"), 500
    except:
        return "<h1>500 - Error del servidor</h1><p>Ha ocurrido un error inesperado</p>", 500

if __name__ == '__main__':
    # Verificar que existan las carpetas necesarias
    carpetas_necesarias = [
        "datos",
        "static",
        "static/imagenes",
        "static/css",
        "static/js",
        "templates"
    ]
    
    for carpeta in carpetas_necesarias:
        try:
            if not os.path.exists(carpeta):
                print(f"ADVERTENCIA: La carpeta '{carpeta}' no existe, creándola...")
                os.makedirs(carpeta, exist_ok=True)
        except Exception as e:
            print(f"ERROR al crear carpeta {carpeta}: {e}")
    
    # Crear subcarpetas para cada zona y verificar contenido
    for zona in ZONAS_DISPONIBLES:
        try:
            zona_path = os.path.join("static", "imagenes", zona)
            if not os.path.exists(zona_path):
                print(f"Creando carpeta para zona: {zona}")
                os.makedirs(zona_path, exist_ok=True)
            else:
                # Verificar contenido de la carpeta
                archivos = os.listdir(zona_path)
                print(f"Carpeta {zona} contiene: {archivos}")
        except Exception as e:
            print(f"ERROR al crear/verificar carpeta para zona {zona}: {e}")
    
    # Verificar archivo Excel
    if not os.path.exists(EXCEL_PATH):
        print(f"ADVERTENCIA: El archivo Excel {EXCEL_PATH} no existe")
        print("Por favor, asegúrate de que el archivo existe antes de usar la aplicación")
    
    print("Iniciando servidor Flask...")
    print(f"Zonas disponibles: {ZONAS_DISPONIBLES}")
    print(f"Ruta del Excel: {EXCEL_PATH}")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"ERROR al iniciar el servidor: {e}")