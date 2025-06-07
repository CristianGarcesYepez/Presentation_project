# scripts/generar_datos.R

# Librerías necesarias
library(DBI)         # Conexión a bases de datos
library(odbc)        # Drivers ODBC para bases de datos
library(readxl)      # Lectura de archivos Excel
library(dplyr)       # Manipulación de datos
library(lubridate)   # Manejo de fechas

# ⚠️ Simulación de datos ficticios (puedes reemplazar esta sección con tu conexión real)

# Ejemplo: datos ficticios simulando la lectura desde Excel o BD
trabajos <- data.frame(
  Zona = c("Africa", "Asia", "Churute", "Korea"),
  Trabajo = c("Revisión de sensores", "Inspección de bombas", "Reparación estructural", "Calibración de equipos"),
  Tipo = c("Mantenimiento", "Inspección", "Reparación", "Calibración"),
  Fecha = as.Date(c("2025-05-10", "2025-05-12", "2025-05-14", "2025-05-16")),
  Días = c(3, 2, 5, 1),
  Avance = c("80%", "100%", "60%", "90%"),
  stringsAsFactors = FALSE
)

# Aquí podrías usar:
# conn <- dbConnect(odbc::odbc(), "NombreDSN")
# trabajos <- dbGetQuery(conn, "SELECT * FROM tabla_trabajos")


# Crear carpeta si no existe
#if (!dir.exists("datos")) dir.create("datos")

# Establecer directorio de trabajo con la sintaxis correcta
setwd("C:/Users/soporte/Desktop/Cristian G/IPSP/Presentation_project/datos")

# Para Excel:
writexl::write_xlsx(trabajos, "trabajos.xlsx")

# Guardar los datos en archivo RDS para el script 2
#saveRDS(trabajos, "datos_generados.rds")
cat("✅ Datos generados y guardados como 'scripts/datos_generados.rds'\n")
