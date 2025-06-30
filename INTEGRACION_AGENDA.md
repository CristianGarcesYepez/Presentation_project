# Integración de Agenda con la Aplicación Principal

## Resumen de la Integración

Se ha integrado exitosamente la funcionalidad de `agenda_app.py` con `app.py`, creando un sistema unificado que permite gestionar tanto los trabajos por zonas como la agenda semanal.

## Nuevas Funcionalidades

### 1. Rutas Agregadas

- **`/agenda`** - Página principal de la agenda semanal
- **`/agenda/datos`** - API endpoint que devuelve datos de agenda en formato JSON
- **`/agenda/actualizar`** - Endpoint para forzar actualización de datos de agenda

### 2. Navegación Mejorada

- **Página de Inicio**: Enlace "CONTINUAR →" ahora dirige a `/agenda`
- **Menú Principal**: Nuevo enlace "Ver Agenda Semanal" para acceso directo
- **Página de Agenda**: Botones de navegación para volver al inicio o ir al menú

### 3. Procesamiento Automático de Datos

- Lectura automática del archivo Excel `datos/datos_agendaEJ.xlsx`
- Generación automática de `datos_agenda.json`
- Cálculo de la semana anterior basado en la fecha actual
- Filtrado de eventos por día de la semana

## Estructura de Archivos Actualizada

```
Presentation_project/
├── app.py                  # Aplicación principal (actualizada)
├── agenda_app.py           # Módulo de agenda (actualizado)
├── datos_agenda.json       # Archivo generado automáticamente
├── datos/
│   └── datos_agendaEJ.xlsx # Archivo Excel con datos de agenda
├── static/
│   └── css/
│       ├── estilo.css          # Estilos principales (actualizado)
│       └── estilo_agenda.css   # Estilos específicos de agenda
└── templates/
    ├── index.html          # Página principal (sin cambios)
    ├── menu.html           # Menú principal (actualizado)
    └── agenda.html         # Página de agenda (actualizada)
```

## Uso de la Aplicación

### Iniciar la Aplicación

```bash
cd "ruta/del/proyecto"
python app.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

### Flujo de Navegación

1. **Página Principal** (`/`) → **Agenda** (`/agenda`)
2. **Agenda** → **Menú** (`/menu`) → **Zonas específicas**
3. **Menú** → **Agenda** (acceso directo)

### APIs Disponibles

#### Obtener Datos de Agenda
```
GET /agenda/datos
```
Respuesta: JSON con datos de la semana anterior organizados por día

#### Actualizar Datos de Agenda
```
GET /agenda/actualizar
```
Respuesta: JSON con estado de la actualización

## Configuración

### Archivo Excel de Agenda

- **Ubicación**: `datos/datos_agendaEJ.xlsx`
- **Columnas requeridas**: `Fecha` + columnas adicionales con información de eventos
- **Formato de fecha**: Compatible con pandas (DD/MM/YYYY, YYYY-MM-DD, etc.)

### Personalización

Para cambiar el archivo Excel fuente, editar en `agenda_app.py`:

```python
def obtener_datos_agenda():
    ruta_excel = "./datos/tu_archivo.xlsx"  # Cambiar aquí
```

## Características Técnicas

### Integración con Flask

- **Función**: `init_agenda_routes(app)` - Registra todas las rutas de agenda
- **Template Filter**: `generar_tabla_agenda()` - Genera HTML de tabla en el servidor
- **Error Handling**: Manejo robusto de errores con páginas de error personalizadas

### Responsividad

- Diseño adaptable para diferentes tamaños de pantalla
- Estilos CSS optimizados para visualización de agenda
- Navegación intuitiva entre secciones

### Rendimiento

- Generación automática de JSON para evitar reprocesamiento
- Carga eficiente de datos desde Excel
- Manejo de errores sin afectar el resto de la aplicación

## Resolución de Problemas

### Archivo Excel No Encontrado

Si aparece el mensaje "archivo no existe":
1. Verificar que `datos/datos_agendaEJ.xlsx` existe
2. Comprobar los permisos de lectura del archivo
3. Actualizar la ruta en `agenda_app.py` si es necesario

### Datos No Aparecen en Agenda

1. Verificar formato de fechas en Excel
2. Asegurar que hay datos para la semana anterior
3. Comprobar que la columna 'Fecha' existe en Excel

### Errores de CSS

Si los estilos no cargan:
1. Verificar que `static/css/estilo_agenda.css` existe
2. Comprobar permisos de archivos estáticos
3. Refrescar el navegador (Ctrl+F5)

## Próximas Mejoras Sugeridas

1. **Editor de Agenda**: Funcionalidad para agregar/editar eventos
2. **Múltiples Semanas**: Visualización de semanas anteriores/posteriores
3. **Exportación**: PDF o Excel de la agenda generada
4. **Filtros**: Por tipo de evento, responsable, etc.
5. **Notificaciones**: Alertas para eventos próximos

## Soporte

Para problemas técnicos:
1. Revisar logs en la consola donde se ejecuta `python app.py`
2. Verificar que todas las dependencias estén instaladas
3. Comprobar versiones de Python y librerías utilizadas
