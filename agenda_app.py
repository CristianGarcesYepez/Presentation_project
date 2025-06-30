#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar datos de Excel y generar agenda semanal
Procesa fechas y determina la semana anterior a la actual
"""

import pandas as pd
import datetime as dt
from datetime import timedelta
import json
import os
from flask import render_template, jsonify

def obtener_semana_anterior():
    """
    Obtiene las fechas de la semana anterior (Lunes a Domingo)
    """
    hoy = dt.date.today()
    # Obtener el lunes de la semana actual
    lunes_actual = hoy - timedelta(days=hoy.weekday())
    # Obtener el lunes de la semana anterior
    lunes_anterior = lunes_actual - timedelta(days=7)
    
    # Generar todas las fechas de la semana anterior
    fechas_semana = []
    for i in range(7):  # 7 días de la semana
        Fecha = lunes_anterior + timedelta(days=i)
        fechas_semana.append(Fecha)
    
    return fechas_semana

def procesar_excel(ruta_archivo):
    """
    Procesa el archivo Excel y extrae datos relevantes
    """
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_archivo)
        
        # Convertir la columna Fecha a datetime si no lo está
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        else:
            print("Advertencia: No se encontró la columna 'Fecha' en el archivo Excel")
            return {}
        
        # Obtener fechas de la semana anterior
        fechas_semana_anterior = obtener_semana_anterior()
        
        # Filtrar datos para la semana anterior
        datos_semana = {}
        
        for Fecha in fechas_semana_anterior:
            # Convertir Fecha a datetime para comparación
            fecha_dt = pd.to_datetime(Fecha)
            
            # Filtrar registros de esta Fecha
            registros_dia = df[df['Fecha'].dt.date == Fecha].copy()
            
            # Determinar número de semana del año
            num_semana = Fecha.isocalendar()[1]
            
            # Preparar datos del día
            datos_dia = {
                'Fecha': Fecha.strftime('%d'),
                'fecha_completa': Fecha.strftime('%Y-%m-%d'),
                'dia_semana': Fecha.strftime('%A'),
                'mes': Fecha.strftime('%B'),
                'num_semana': num_semana,
                'eventos': []
            }
            
            # Procesar eventos/registros del día
            for _, registro in registros_dia.iterrows():
                evento = {}
                for columna in df.columns:
                    if columna != 'Fecha':
                        valor = registro[columna]
                        if pd.notna(valor):
                            evento[columna] = str(valor)
                
                if evento:  # Solo agregar si hay datos
                    datos_dia['eventos'].append(evento)
            
            # Usar día de la semana en español como clave
            dias_es = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes', 
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            
            dia_clave = dias_es.get(datos_dia['dia_semana'], datos_dia['dia_semana'])
            datos_semana[dia_clave] = datos_dia
        
        return datos_semana
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {ruta_archivo}")
        return {}
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return {}

def generar_json_datos(datos_semana):
    """
    Genera archivo JSON con los datos procesados
    """
    try:
        with open('datos_agenda.json', 'w', encoding='utf-8') as f:
            json.dump(datos_semana, f, ensure_ascii=False, indent=2, default=str)
        print("Archivo datos_agenda.json generado exitosamente")
    except Exception as e:
        print(f"Error al generar JSON: {str(e)}")

def obtener_datos_agenda():
    """
    Función para obtener datos de agenda procesados
    """
    # CONFIGURAR AQUÍ LA RUTA DEL ARCHIVO EXCEL
    ruta_excel = "./datos/datos_agendaEJ.xlsx"  # Cambiar por la ruta real del archivo
    
    # Verificar si el archivo existe
    if not os.path.exists(ruta_excel):
        print(f"ATENCIÓN: El archivo {ruta_excel} no existe.")
        return {}
    
    # Procesar datos del Excel
    datos_semana = procesar_excel(ruta_excel)
    
    if datos_semana:
        # Generar archivo JSON para usar en HTML
        generar_json_datos(datos_semana)
        return datos_semana
    else:
        print("No se pudieron procesar los datos del archivo Excel")
        return {}

def generar_html_tabla_agenda(datos_agenda):
    """
    Genera el HTML de la tabla de agenda a partir de los datos procesados
    """
    try:
        fechas_semana = obtener_semana_anterior()
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dias_abrev = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
        
        html = '''
        <table class="agenda-table">
            <thead>
                <tr>
                    <td colspan="7" class="header-main">
                        VISITAS A ZONAS - EJECUCIÓN PLANIFICACIÓN
                    </td>
                </tr>
                <tr>'''
        
        # Generar encabezados de días
        for dia_abrev in dias_abrev:
            html += f'<td class="header-days">{dia_abrev}</td>'
        
        html += '''</tr>
                <tr class="date-row">'''
        
        # Generar celdas de fechas
        for i, fecha in enumerate(fechas_semana):
            dia = fecha.day
            is_highlight = i == 0 or i == 6  # Destacar lunes y domingo
            clase_highlight = ' highlight' if is_highlight else ''
            html += f'<td class="date-cell{clase_highlight}">{dia}</td>'
        
        html += '''</tr>
            </thead>
            <tbody>
                <tr>'''
        
        # Generar celdas de contenido
        for i, fecha in enumerate(fechas_semana):
            dia_semana = dias_semana[i]
            
            html += '<td class="content-cell">'
            
            # Buscar eventos para este día
            datos_del_dia = datos_agenda.get(dia_semana, {})
            eventos = datos_del_dia.get('eventos', [])
            
            if eventos and len(eventos) > 0:
                for evento in eventos:
                    html += '<div class="evento">'
                    
                    # Mostrar todos los campos del evento
                    for campo, valor in evento.items():
                        if valor and str(valor).strip():
                            html += f'<div class="evento-titulo">{campo}:</div>'
                            html += f'<div class="evento-detalle">{valor}</div>'
                    
                    html += '</div>'
            else:
                html += '<div class="sin-eventos">Sin eventos programados</div>'
            
            html += '</td>'
        
        html += '''</tr>
            </tbody>
        </table>'''
        
        return html
        
    except Exception as e:
        print(f"Error al generar HTML de tabla: {e}")
        return f'<div class="error">Error al generar tabla de agenda: {str(e)}</div>'

def init_agenda_routes(app):
    """
    Inicializa las rutas relacionadas con la agenda en la aplicación Flask
    """
    
    # Registrar función personalizada para Jinja2
    @app.template_global()
    def generar_tabla_agenda(datos_agenda):
        return generar_html_tabla_agenda(datos_agenda)
    
    @app.route('/agenda')
    def mostrar_agenda():
        """
        Ruta para mostrar la página de agenda semanal
        """
        try:
            # Obtener datos de agenda actualizados
            datos_agenda = obtener_datos_agenda()
            
            # Generar información de la semana
            fechas_semana = obtener_semana_anterior()
            if fechas_semana:
                fecha_inicio = fechas_semana[0]
                fecha_fin = fechas_semana[6]
                semana_numero = fecha_inicio.isocalendar()[1]
                año = fecha_inicio.year
                
                info_semana = {
                    'numero': semana_numero,
                    'año': año,
                    'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                    'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                    'mes': fecha_inicio.strftime('%B')
                }
            else:
                info_semana = {
                    'numero': 0,
                    'año': dt.date.today().year,
                    'fecha_inicio': '',
                    'fecha_fin': '',
                    'mes': ''
                }
            
            return render_template('agenda.html', 
                                 datos_agenda=datos_agenda,
                                 info_semana=info_semana)
        
        except Exception as e:
            print(f"ERROR en mostrar_agenda: {e}")
            try:
                return render_template("error.html", 
                                     mensaje="Error al cargar la agenda",
                                     detalle=str(e)), 500
            except:
                return f"<h1>Error al cargar la agenda</h1><p>{str(e)}</p>", 500
    
    @app.route('/agenda/datos')
    def datos_agenda_json():
        """
        API endpoint para obtener datos de agenda en formato JSON
        """
        try:
            datos_agenda = obtener_datos_agenda()
            return jsonify(datos_agenda)
        except Exception as e:
            print(f"ERROR en datos_agenda_json: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/agenda/actualizar')
    def actualizar_agenda():
        """
        Endpoint para forzar actualización de datos de agenda
        """
        try:
            datos_agenda = obtener_datos_agenda()
            if datos_agenda:
                return jsonify({
                    "status": "success", 
                    "message": "Agenda actualizada correctamente",
                    "datos": datos_agenda
                })
            else:
                return jsonify({
                    "status": "error", 
                    "message": "No se pudieron actualizar los datos"
                }), 500
        except Exception as e:
            print(f"ERROR en actualizar_agenda: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

def main():
    """
    Función principal del script
    """
    # CONFIGURAR AQUÍ LA RUTA DEL ARCHIVO EXCEL
    ruta_excel = "./datos/datos_agendaEJ.xlsx"  # Cambiar por la ruta real del archivo
    
    print("Iniciando procesamiento de agenda semanal...")
    print(f"Archivo a procesar: {ruta_excel}")
    
    # Verificar si el archivo existe
    if not os.path.exists(ruta_excel):
        print(f"ATENCIÓN: El archivo {ruta_excel} no existe.")
        print("Por favor, actualiza la variable 'ruta_excel' con la ruta correcta.")
        return
    
    # Procesar datos del Excel
    datos_semana = procesar_excel(ruta_excel)
    
    if datos_semana:
        print("Datos procesados exitosamente:")
        for dia, info in datos_semana.items():
            print(f"  {dia}: {info['Fecha']} ({len(info['eventos'])} eventos)")
        
        # Generar archivo JSON para usar en HTML
        generar_json_datos(datos_semana)
        
        print("\nProcesamiento completado. Los datos están listos para mostrar en agenda.html")
    else:
        print("No se pudieron procesar los datos del archivo Excel")

if __name__ == "__main__":
    main()