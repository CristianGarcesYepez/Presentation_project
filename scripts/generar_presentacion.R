---
  title: "Informe de Avance por Zona"
format:
  html:
  toc: true
toc-title: "Contenido"
toc-depth: 2
number-sections: true
theme: cosmo
css: styles.css
lang: es
execute:
  echo: false
warning: false
message: false
---
  
```{r setup}
library(readr)
library(dplyr)
library(glue)
library(kableExtra)

# Cargar datos desde el archivo generado
trabajos <- readRDS("scripts/datos_generados.rds")

# Obtener zonas únicas
zonas <- unique(trabajos$zona)
```

# Hoja de Presentación

<center>
  <h1 style="color:#102030;">Informe de Avances por Zona</h1>
  <h3>Fecha de generación: `r Sys.Date()`</h3>
  </center>
  
  ---
  
  ## Introducción
  
  Este informe presenta el avance de los trabajos distribuidos por zona geográfica. Cada sección incluye:
  
  - Una imagen representativa de la zona.
- Una tabla con información clave: trabajo, tipo, fecha, días y porcentaje de avance.

---
  
  ## Zonas
  
  ```{r generar-zonas, results='asis'}
for (zona in zonas) {
  subtitulo <- glue("### Zona: {zona}")
  imagen <- glue("<img src='imagenes/{zona}.jpg' style='width:100%; max-height:300px; object-fit:cover; margin-bottom:15px;'>")
  
  tabla_zona <- trabajos %>%
    filter(zona == !!zona) %>%
    select(trabajo, tipo, fecha, dias, avance) %>%
    mutate(avance = paste0(avance, "%")) %>%
    kable("html", escape = FALSE, align = "c", col.names = c("Trabajo", "Tipo", "Fecha", "Días", "% Avance")) %>%
    kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = F) %>%
    row_spec(0, background = "#102030", color = "white")
  
  cat(subtitulo, "\n", imagen, "\n")
  print(tabla_zona)
  cat("\n\n---\n")
}