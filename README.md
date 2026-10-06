# Proyecto Sample Superstore

Análisis exploratorio de datos (EDA) del dataset **Sample Superstore** para responder la
pregunta de negocio: **¿qué factores (categoría, región, segmento) explican el nivel de ventas?**

## Contenido

Una app **Dash** con una pestaña por sección (introducción, contexto,
EDA, conclusiones…). La pestaña **Dashboard** muestra el dashboard 3D (`3DWebDashboard/`), cuyos
gráficos se definen con **Plotly** en `dashboard/build_dashboard.py`.

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

## Dashboard de ventas (Python + Plotly)

Resume el EDA con el formato de un dashboard ejecutivo: cabecera con filtros, KPIs, secciones y
un **insight** debajo de cada gráfico. Sin filtros, el insight es el texto del EDA (`TEXTOS` en
`tabs/eda.py`); con filtros, una lectura equivalente calculada con los datos filtrados.

- **Filtros** por categoría, región, segmento y año que actualizan todo el dashboard.
- **KPIs:** ventas, pedidos, media, mediana y máximo de `Sales`, con variación frente al año anterior.
- **Distribución de ventas:** histograma de `Sales` y % de pedidos vs. % de ventas por categoría,
  región y segmento.
- **Ventas por categoría, región y segmento:** boxplots.
- **Relación entre variables:** pedidos por categoría y región, bins 2D de `Discount` vs. `Sales` y
  matriz de correlación.
- **Geografía y tendencia:** pedidos por estado, evolución mensual y tendencia por categoría.
- **Calidad de datos:** faltantes, duplicados y atípicos (IQR).

`dashboard/build_dashboard.py` define las figuras con Plotly y genera dos archivos:

- `3DWebDashboard/dashboard_data.json`: figuras y datos que lee el dashboard 3D.
- `assets/dashboard.html`: el mismo dashboard (tema claro) en un solo archivo que se abre sin
  servidor, para compartirlo por separado.

Los dos usan la misma lógica de filtros, KPIs e insights: `3DWebDashboard/dashboard_core.js`.

Para regenerarlos (por ejemplo, después de cambiar los datos):

```powershell
python dashboard/build_dashboard.py            # usa plotly.js desde CDN
python dashboard/build_dashboard.py --offline  # incrusta plotly.js en assets/dashboard.html (~4 MB)
```

## Dashboard 3D (`3DWebDashboard/`)

La pestaña **Dashboard** muestra `3DWebDashboard/3DWebDashboard.html`: una portada 3D (anillo de
tarjetas con las cifras principales) que abre la vista de gráficos `Dashboard Superstore.dc.html`.
Las dos leen `dashboard_data.json`, así que regenerarlo también actualiza el 3D.

`app.py` sirve esta carpeta en **http://127.0.0.1:8050/3d/3DWebDashboard.html** (fuera de `assets/`
para que Dash no cargue `support.js` en la app) y genera `dashboard_data.json` si falta. La carpeta
también funciona sola en cualquier servidor estático (por ejemplo GitHub Pages o
`python -m http.server`). Necesita internet (React, Plotly y fuentes vienen de CDN) y no funciona
abriendo el archivo con doble clic.

## Datos

Los datos ya vienen procesados, así que no hace falta regenerarlos para correr el proyecto.
Si modificas el CSV original, vuelve a generarlos así:

```powershell
python data/generate_data.py          # data/raw/Sample - Superstore.csv  ->  data/superstore_transformado.csv
python dashboard/build_dashboard.py   # superstore_transformado.csv       ->  dashboard_data.json y dashboard.html
```

## Estructura

```
├── app.py                 # Punto de entrada de la app Dash
├── common.py              # Utilidades compartidas entre pestañas
├── requirements.txt       # Dependencias de Python
├── tabs/                  # Una pestaña por archivo, cada una expone layout()
├── 3DWebDashboard/        # Dashboard 3D (servido por app.py en /3d/)
│   ├── dashboard_core.js  # Filtros, KPIs e insights (compartido con assets/dashboard.html)
│   └── dashboard_data.json # Figuras y datos generados (no editar a mano)
├── assets/
│   ├── style.css          # Estilos de la app Dash
│   └── dashboard.html     # Dashboard generado (no editar a mano)
├── dashboard/
│   ├── build_dashboard.py # Define las figuras con Plotly y genera los dos archivos
│   └── template.html      # Plantilla HTML/CSS del dashboard autocontenido
└── data/
    ├── raw/               # Dataset original
    ├── generate_data.py   # Limpieza y transformación
    └── superstore_transformado.csv
```

## Problemas comunes

- **La pestaña Dashboard no muestra gráficos:** plotly.js se carga desde un CDN, así que hace falta
  internet. Para ver el dashboard sin conexión, genera `assets/dashboard.html` con
  `python dashboard/build_dashboard.py --offline` y ábrelo directamente.
- **`python` no se reconoce en Windows:** prueba con `py app.py` y `py -m pip install -r requirements.txt`.
- **El puerto 8050 está ocupado:** cierra el otro proceso que lo esté usando.

---

Proyecto: Alex Teran y David Estrada
