# Dashboard de ventas — Sample Superstore

Dashboard interactivo (React + TanStack Start + Tailwind) con las visualizaciones e insights
que responden a la pregunta de negocio del proyecto: **¿qué factores (categoría, región,
segmento) explican el nivel de ventas del dataset Sample Superstore?**

Es parte del proyecto más grande **proyecto_samplesuperstore**: aquí vive la sección
"Dashboard" (visualizaciones interactivas + un asistente de IA que responde preguntas de
negocio sobre los mismos datos); el resto del contexto, objetivos, metodología y
conclusiones del EDA está en la app principal (Dash) y en el libro `rbook-main/`.

Cada gráfico trae su insight justo debajo, y un botón "Profundizar con IA" que abre el chat
con esa pregunta precargada.

## Datos

`src/data/superstore.json` se genera con `data/export_json.py` (raíz del proyecto) a partir
de `data/superstore_transformado.csv`, sin alterar ningún valor. También se puede cargar
un CSV propio desde el botón "Actualizar datos" (columnas esperadas: Category, Region,
Segment, Sales, Quantity, Discount, Profit).

## Asistente de IA

El chat usa la API de Anthropic (Claude). Necesitas una API key en `ANTHROPIC_API_KEY`:

```sh
cp .env.example .env
# edita .env y pega tu API key (console.anthropic.com)
```

Sin la key configurada, el resto del dashboard funciona igual — solo el chat responde con
un error.

## Desarrollo

```sh
npm i
npm run dev
```

## Build y ejecución en producción

```sh
npm run build
node .output/server/index.mjs
```

## Stack

- TanStack Start (React 19 + Vite + SSR, para poder servir `/api/chat`)
- Tailwind CSS v4
- TypeScript
- Anthropic SDK (`@anthropic-ai/sdk`)
