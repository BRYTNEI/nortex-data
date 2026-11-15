"""Datos locales sin API: reservorio, PCR, turnos, ENFEN, economía, suelo de laboratorio,
riego de la parcela e historial (v0.7 V-19…V-40, RF-23).

Se leen desde CSV con columnas fijas en ``NORTEX_LOCAL_DIR`` (por defecto ``data/local``,
ignorada por Git). Las plantillas con una fila de ejemplo están en ``plantillas/``: copie el
archivo, borre la fila ``EJEMPLO`` y complete con datos de ANA, la Junta de Usuarios, ENFEN,
SIEA o el laboratorio. Cada fila conserva su ``fuente`` en ``product``.

Categoría (v0.7 §6.1) en ``qc_flag``: ``observado`` para registros de organismos (ANA,
caudales) y ``declarado`` para lo que informa el usuario o la Junta.
"""

import logging
import os
from pathlib import Path

import pandas as pd

from nortex_data.utils.core import config, frame, row, variables_for

_log = logging.getLogger(__name__)

#: plantilla → (columna de fecha, categoría, {variable: columna de valor}, columnas de etiqueta)
TEMPLATES = {
    "reservorio": ("fecha", "observado", {"reservoir_volume": "volumen_hm3"}, []),
    "caudal_quiroz": ("fecha", "observado", {"quiroz_flow": "caudal_m3s"}, []),
    "pcr": ("fecha_inicio", "declarado",
            {"pcr_area_authorized": "area_autorizada_ha", "water_allocation": "dotacion_m3_ha"},
            ["campania", "comision", "cultivo"]),
    "turnos": ("fecha_inicio", "declarado", {"turn_interval": "intervalo_dias"}, ["comision"]),
    "enfen": ("fecha_emision", "declarado",
              {"enfen_alert_state": "codigo_alerta", "enfen_prob_nino": "prob_nino_costero_pct"},
              ["estado_alerta", "horizonte"]),
    "economia": ("anio", "declarado",
                 {"yield_reference": "rendimiento_t_ha", "price_farmgate": "precio_chacra_soles_kg",
                  "cost_production": "costo_soles_ha"},
                 ["campania", "cultivo", "ambito"]),
    "suelo_laboratorio": ("fecha_muestreo", "declarado",
                          {"lab_theta_fc": "theta_fc", "lab_theta_wp": "theta_wp", "lab_ph": "ph",
                           "soil_ec": "ece_dsm", "soil_om": "mo_pct", "water_ec": "ecw_dsm",
                           "water_table_depth": "napa_m",
                           "soil_effective_depth": "profundidad_efectiva_m"},
                          ["textura", "profundidad_cm"]),
    "riego_parcela": ("fecha", "declarado", {"application_efficiency": "eficiencia"},
                      ["sistema", "comision"]),
    "historial": ("fecha_siembra", "declarado", {"history_yield": "rendimiento_t_ha"},
                  ["campania", "cultivo", "fecha_cosecha"]),
}


def local_dir():
    """Carpeta de los CSV locales."""
    return Path(os.getenv("NORTEX_LOCAL_DIR", "data/local"))


def template_columns(name):
    """Columnas obligatorias de una plantilla."""
    date_col, _, values, labels = TEMPLATES[name]
    extra = ["aoi_id"] if name in {"suelo_laboratorio", "riego_parcela", "historial"} else []
    return [date_col, *extra, *labels, *values.values(), "fuente"]


def read_template(name, path, aoi, selected, catalog):
    """Lee una plantilla y devuelve filas del esquema común para el AOI."""
    date_col, category, values, labels = TEMPLATES[name]
    table = pd.read_csv(path, dtype=str).fillna("")
    missing = [c for c in template_columns(name) if c not in table.columns]
    if missing:
        raise ValueError(f"{path}: faltan columnas {missing}; use plantillas/{name}.csv")
    table = table[table["fuente"].str.upper() != "EJEMPLO"]
    if "aoi_id" in table:
        table = table[table["aoi_id"].isin(["", aoi["aoi_id"]])]
    rows = []
    for _, record in table.iterrows():
        raw_date = record[date_col]
        day = pd.Timestamp(year=int(raw_date), month=1, day=1) if date_col == "anio" else pd.Timestamp(raw_date)
        label = " / ".join([record["fuente"], *(f"{c}={record[c]}" for c in labels if record[c])])
        for key, column in values.items():
            if key in selected and record[column] != "":
                rows.append(row(aoi, "local", label, key, day, record[column],
                                catalog[key]["unit"], f"{category};archivo={name}"))
    return rows


def fetch(aoi, start, end, variables=None):
    """Datos declarados u observados localmente para el AOI."""
    selected = variables_for("local", variables)
    if not selected:
        return frame()
    catalog = config("variables")
    rows = []
    for name, (_, _, values, _) in TEMPLATES.items():
        wanted = set(values) & set(selected)
        if not wanted:
            continue
        path = local_dir() / f"{name}.csv"
        if not path.is_file():
            message = (f"Falta {path}: copie plantillas/{name}.csv y complételo "
                       f"(variables {sorted(wanted)})")
            if variables is not None:
                raise FileNotFoundError(message)
            _log.warning(message)
            continue
        rows.extend(read_template(name, path, aoi, wanted, catalog))
    data = frame(rows)
    if start is not None:
        data = data[data.date >= pd.Timestamp(start)]
    if end is not None:
        data = data[data.date <= pd.Timestamp(end)]
    return data.reset_index(drop=True)
