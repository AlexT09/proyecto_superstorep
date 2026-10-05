# Proyecto Sample Superstore

Análisis exploratorio de datos (EDA) del dataset **Sample Superstore** para responder la
pregunta de negocio: **¿qué factores (categoría, región, segmento) explican el nivel de ventas?**

Todo el proyecto es Python: una app **Dash** con una pestaña por sección (introducción, contexto,
EDA, conclusiones…). La pestaña **Dashboard** muestra un dashboard de ventas interactivo
generado con **Plotly** como un HTML autocontenido (`assets/dashboard.html`).

## Requisitos

- **Python** 3.10 o superior

## Cómo correr el proyecto

```powershell
python -m venv .venv
.venv\Scripts\activate       # en macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Después abre **http://127.0.0.1:8050** en el navegador.

## Dashboard de ventas (Python + Plotly → HTML)

`dashboard/build_dashboard.py` lee el dataset transformado, construye las figuras con Plotly y las
incrusta en `dashboard/template.html`. El resultado es `assets/dashboard.html`: un solo archivo que
se abre en cualquier navegador sin servidor, así que también sirve para compartirlo por separado.

Resume los resultados del EDA según los objetivos del proyecto:

- **Filtros** por categoría, región, segmento y año que actualizan todo el dashboard.
- **KPIs:** pedidos, media, mediana y máximo de `Sales` (resumen estadístico del EDA).
- **Hallazgos del EDA** (los de las secciones EDA y Conclusiones).
- Distribución de `Sales`, pedidos y `Sales` por categoría, región y segmento, correlación entre
  variables numéricas y ventas mensuales por categoría.

Para regenerarlo (por ejemplo, después de cambiar los datos):

```powershell
python dashboard/build_dashboard.py            # usa plotly.js desde CDN (~480 KB)
python dashboard/build_dashboard.py --offline  # incrusta plotly.js para verlo sin internet (~4 MB)
```

Si `assets/dashboard.html` no existe, la pestaña Dashboard lo genera al abrirse.

## Dashboard 3D (`3DWebDashboard/`)

La pestaña **Dashboard** muestra `3DWebDashboard/3DWebDashboard.html`: una portada 3D (anillo de
tarjetas con los KPIs) que abre la vista de gráficos `Dashboard Superstore.dc.html`. Esa vista lee
las figuras y los datos de `assets/dashboard.html`, así que regenerarlo también actualiza el 3D.

`app.py` sirve esta carpeta en **http://127.0.0.1:8050/3d/3DWebDashboard.html** (fuera de `assets/`
para que Dash no cargue `support.js` en la app). Necesita servidor e internet (React, Plotly y
fuentes vienen de CDN), por eso no funciona abriendo el archivo con doble clic.

## Datos

Los datos ya vienen procesados, así que no hace falta regenerarlos para correr el proyecto.
Si modificas el CSV original, vuelve a generarlos así:

```powershell
python data/generate_data.py          # data/raw/Sample - Superstore.csv  ->  data/superstore_transformado.csv
python dashboard/build_dashboard.py   # superstore_transformado.csv       ->  assets/dashboard.html
```

## Estructura

```
├── app.py                 # Punto de entrada de la app Dash
├── common.py              # Utilidades compartidas entre pestañas
├── requirements.txt       # Dependencias de Python
├── tabs/                  # Una pestaña por archivo, cada una expone layout()
├── 3DWebDashboard/        # Dashboard 3D (servido por app.py en /3d/)
├── assets/
│   ├── style.css          # Estilos de la app Dash
│   └── dashboard.html     # Dashboard generado (no editar a mano)
├── dashboard/
│   ├── build_dashboard.py # Genera assets/dashboard.html con Plotly
│   └── template.html      # Plantilla HTML/CSS/JS del dashboard
└── data/
    ├── raw/               # Dataset original
    ├── generate_data.py   # Limpieza y transformación
    └── superstore_transformado.csv
```

## Problemas comunes

- **La pestaña Dashboard no muestra gráficos:** el HTML carga plotly.js desde un CDN. Sin internet,
  genera la versión offline con `python dashboard/build_dashboard.py --offline`.
- **`python` no se reconoce en Windows:** prueba con `py app.py` y `py -m pip install -r requirements.txt`.
- **El puerto 8050 está ocupado:** cierra el otro proceso que lo esté usando.

---

Proyecto: Alex Teran y David Estrada
