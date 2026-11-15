"""Índices ENSO: ICEN (ENFEN, costa norte del Perú) y ONI (NOAA, Pacífico central).

Son índices regionales y mensuales de pocos KB: se devuelve todo el registro (desde 1950)
porque la v0.7 los usa para clasificar años históricos y elegir años análogos (§6.3), lo que
exige más de 10 años. ``start``/``end`` recortan si se indican.
"""

import pandas as pd

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import request

#: Mes central de cada estación trimestral del ONI (DJF → enero, ..., NDJ → diciembre).
_ONI_CENTER = {s: i + 1 for i, s in enumerate(
    ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"])}


def parse_icen(text):
    """Lee el archivo oficial del ICEN (líneas ``año mes valor``; comentarios con ``%``)."""
    records = []
    for line in text.splitlines():
        parts = line.split()
        if not parts or line.lstrip().startswith("%") or len(parts) < 3:
            continue
        year, month, value = int(parts[0]), int(parts[1]), float(parts[2])
        records.append((pd.Timestamp(year=year, month=month, day=1), value))
    if not records:
        raise ValueError("ICEN: el archivo no contiene datos")
    return records


def parse_oni(text):
    """Lee la tabla ONI de NOAA CPC (``SEAS YR TOTAL ANOM``); fecha = mes central."""
    records = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[0] not in _ONI_CENTER:
            continue
        month = _ONI_CENTER[parts[0]]
        records.append((pd.Timestamp(year=int(parts[1]), month=month, day=1), float(parts[3])))
    if not records:
        raise ValueError("ONI: el archivo no contiene datos")
    return records


def fetch(aoi, start, end, variables=None):
    """Devuelve ICEN y ONI mensuales (índices regionales, iguales para todos los AOI)."""
    selected = variables_for("enso", variables)
    if not selected:
        return frame()
    settings = config("sources")["enso"]
    catalog = config("variables")
    rows = []
    for key, parser in (("icen", parse_icen), ("oni", parse_oni)):
        if key not in selected:
            continue
        text = request("GET", settings[f"{key}_url"]).text
        for day, value in parser(text):
            if start is not None and day < pd.Timestamp(start).replace(day=1):
                continue
            if end is not None and day > pd.Timestamp(end):
                continue
            rows.append(row(aoi, "enso", catalog[key]["product"], key, day, value,
                            catalog[key]["unit"], "regional_index"))
    return frame(rows)
