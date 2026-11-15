"""Estación meteorológica de referencia: NOAA GSOD (aeropuerto de Piura, OMM 84401).

Uso en la v0.7: validar POWER e IMERG (§7.3, §19) y declarar el sesgo de las mínimas
(§9.6). SENAMHI no tiene API pública; esta estación oficial se publica en la API abierta de
NOAA NCEI. Las filas llevan las coordenadas **de la estación**, no del AOI, y la distancia en
``qc_flag``: es un dato observado puntual, no de la parcela.

Conversiones: °F → °C, pulgadas → mm, nudos → m/s. Códigos de ausencia de GSOD → NaN. Una
precipitación 0,00 con atributo ``I`` (la estación no reportó) se trata como faltante.
"""

import io
import math

import pandas as pd

from nortex_data.utils.blocks import cached_block, concat_blocks
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.http import request

_MISSING = {"MAX": 9999.9, "MIN": 9999.9, "TEMP": 9999.9, "DEWP": 9999.9,
            "PRCP": 99.99, "WDSP": 999.9}
_CONVERT = {
    "station_tmax": ("MAX", lambda v: (v - 32) * 5 / 9),
    "station_tmin": ("MIN", lambda v: (v - 32) * 5 / 9),
    "station_tmean": ("TEMP", lambda v: (v - 32) * 5 / 9),
    "station_dewpoint": ("DEWP", lambda v: (v - 32) * 5 / 9),
    "station_precip": ("PRCP", lambda v: v * 25.4),
    "station_wind": ("WDSP", lambda v: v * 0.514444),
}


def parse_gsod(text, selected, station_aoi, product, catalog, distance_km):
    """Convierte el CSV de NCEI (global-summary-of-the-day) en filas del esquema común."""
    table = pd.read_csv(io.StringIO(text), dtype=str)
    rows = []
    for _, record in table.iterrows():
        day = pd.Timestamp(record["DATE"])
        for key in selected:
            column, convert = _CONVERT[key]
            raw = pd.to_numeric(str(record.get(column, "")).strip(), errors="coerce")
            flag = f"station;distance_km={distance_km:.0f}"
            if pd.isna(raw) or raw == _MISSING[column]:
                value = float("nan")
            elif key == "station_precip" and str(record.get("PRCP_ATTRIBUTES", "")).strip() == "I":
                value, flag = float("nan"), flag + ";precip_not_reported"
            else:
                value = convert(raw)
            rows.append(row(station_aoi, "estacion", product, key, day, value,
                            catalog[key]["unit"], flag))
    return frame(rows)


def fetch(aoi, start, end, variables=None):
    """Serie diaria de la estación de referencia (regla de 10 años, bloques anuales)."""
    selected = variables_for("estacion", variables)
    if not selected:
        return frame()
    settings = config("sources")["estacion"]
    catalog = config("variables")
    start, end = bounds(settings["first"], start, end)
    station_aoi = {"aoi_id": aoi["aoi_id"], "lat": settings["lat"], "lon": settings["lon"]}
    r = math.radians
    distance_km = 6371 * math.acos(min(1, math.sin(r(aoi["lat"])) * math.sin(r(settings["lat"]))
                                       + math.cos(r(aoi["lat"])) * math.cos(r(settings["lat"]))
                                       * math.cos(r(aoi["lon"] - settings["lon"]))))
    product = f'NOAA GSOD {settings["station"]} ({settings["name"]})'

    def block(begin, stop):
        params = {
            "dataset": "global-summary-of-the-day", "stations": settings["station"],
            "startDate": f"{begin:%Y-%m-%d}", "endDate": f"{stop:%Y-%m-%d}",
            "format": "csv", "includeAttributes": "true",
        }
        text = request("GET", settings["endpoint"], params=params).text
        return parse_gsod(text, selected, station_aoi, product, catalog, distance_km)

    return concat_blocks(
        cached_block("estacion", aoi, begin, stop, [settings["station"], sorted(selected)], block)
        for begin, stop in years(start, end)
    )
