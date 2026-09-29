"""tabs/metodologia.py — ETL: extracción, transformación y carga de los datos."""
import dash_bootstrap_components as dbc
from dash import dcc, html

from common import load_data, page_header, soft_card

ETL_CODE = '''library(tidyverse)

# --- Extracción ---
df <- read_csv(
  "Sample - Superstore.csv",
  locale = locale(encoding = "latin1")
)

# --- Transformación ---
df <- df %>%
  mutate(
    `Order Date` = mdy(`Order Date`),
    `Ship Date`  = mdy(`Ship Date`)
  ) %>%
  rename(Order_Date = `Order Date`) %>%
  arrange(Order_Date)

# --- Carga ---
write_csv(df, "superstore_transformado.csv")'''


def layout():
    df = load_data()
    return html.Div([
        page_header("Metodología", "ETL: de los datos crudos al dataset transformado"),
        dbc.Row([
            dbc.Col(soft_card("ETL", [
                dcc.Markdown(f"```r\n{ETL_CODE}\n```"),
                html.P(f"Fuente: Sample - Superstore ({len(df):,} filas). Se convierten Order Date y Ship Date "
                       "de texto a fecha usando mdy() de lubridate (formato mes/día/año, como vienen en el "
                       "archivo), y con arrange() se ordenan las filas por fecha de pedido."),
            ], "blue"), md=12, className="mb-3"),
        ]),
    ])
