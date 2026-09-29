# Proyecto Sample Superstore

Análisis exploratorio de datos (EDA) del dataset **Sample Superstore** para responder la
pregunta de negocio: **¿qué factores (categoría, región, segmento) explican el nivel de ventas?**

El proyecto tiene dos aplicaciones que trabajan juntas:

| Parte | Carpeta | Tecnología | URL local |
|---|---|---|---|
| App principal (introducción, contexto, EDA, conclusiones…) | raíz (`app.py`, `tabs/`) | Python · Dash · Plotly | http://127.0.0.1:8050 |
| Dashboard interactivo + asistente de IA | `dash-src/` | React · TanStack Start · Vite | http://localhost:5173 |

La pestaña **Dashboard** de la app Dash muestra el dashboard de React en un iframe que apunta a
`http://localhost:5173/`. Si el dashboard de React no está corriendo, esa pestaña aparece en blanco.
Todo lo demás funciona sin él.

## Requisitos

- **Python** 3.10 o superior
- **Node.js** 20 o superior (incluye npm)
- *(Opcional)* Una API key de Anthropic para el chat de IA del dashboard

## Cómo correr el proyecto

Abre **dos terminales** en la carpeta del proyecto.

### Terminal 1: dashboard React

```powershell
cd dash-src
npm install
copy .env.example .env      # en macOS/Linux: cp .env.example .env
npm run dev
```

Queda disponible en http://localhost:5173.

> Para el chat de IA, edita `dash-src/.env` y pega tu key en `ANTHROPIC_API_KEY`
> (se obtiene en console.anthropic.com). Sin la key, el dashboard funciona igual y solo el chat
> responde con un error.

### Terminal 2: app principal (Dash)

```powershell
python -m venv .venv
.venv\Scripts\activate       # en macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Después abre **http://127.0.0.1:8050** en el navegador.

## Datos

Los datos ya vienen procesados, así que no hace falta regenerarlos para correr el proyecto.
Si modificas el CSV original, vuelve a generarlos así:

```powershell
python data/generate_data.py   # data/raw/Sample - Superstore.csv  ->  data/superstore_transformado.csv
python data/export_json.py     # superstore_transformado.csv       ->  dash-src/src/data/superstore.json
```

## Build de producción del dashboard (opcional)

```powershell
cd dash-src
npm run build
$env:PORT=5173; node .output/server/index.mjs   # macOS/Linux: PORT=5173 node .output/server/index.mjs
```

El servidor de producción usa el puerto 3000 por defecto. Se fija en 5173 para que el iframe de
Dash lo encuentre.

## Estructura

```
├── app.py                 # Punto de entrada de la app Dash
├── common.py              # Utilidades compartidas entre pestañas
├── requirements.txt       # Dependencias de Python
├── tabs/                  # Una pestaña por archivo, cada una expone layout()
├── assets/style.css       # Estilos de la app Dash
├── data/
│   ├── raw/               # Dataset original
│   ├── generate_data.py   # Limpieza y transformación
│   ├── export_json.py     # Exporta JSON para el dashboard React
│   └── superstore_transformado.csv
└── dash-src/              # Dashboard React (más detalles en dash-src/README.md)
```

## Problemas comunes

- **La pestaña Dashboard se ve en blanco:** el dashboard React no está corriendo en el puerto 5173
  (ver Terminal 1).
- **`npm` o `node` no se reconocen:** instala Node.js desde nodejs.org y reabre la terminal.
- **`python` no se reconoce en Windows:** prueba con `py app.py` y `py -m pip install -r requirements.txt`.
- **El puerto 5173 u 8050 está ocupado:** cierra el otro proceso que lo esté usando.

---

Proyecto: Alex Teran y David Estrada
