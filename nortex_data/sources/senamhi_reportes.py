"""Volumen de reservorios desde los reportes hidrológicos diarios de SENAMHI (PDF).

SENAMHI publica «Información hidrológica diaria» (monitoreo a nivel nacional) con una tabla
de reservorios: «Chira San Lorenzo <volumen MMC> <% capacidad> <capacidad útil MMC>». Los
datos provienen del Proyecto Especial Chira Piura y de la Junta de Usuarios San Lorenzo.
No hay API: se leen los PDF públicos indicados en ``config/sources.yaml`` (``reportes``) y
los que se guarden en ``NORTEX_REPORTES_DIR`` (por defecto ``data/local/reportes_senamhi``).

Cada PDF pesa ~300 KB y se procesa en memoria; no se guarda en disco. Categoría: observado.
"""

import io
import logging
import os
import re
from pathlib import Path

import pandas as pd

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import request

_log = logging.getLogger(__name__)
_MESES = {m: i + 1 for i, m in enumerate(
    ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"])}
_MESES["setiembre"] = 9
_FECHA = re.compile(r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+del?\s+(\d{4})", re.IGNORECASE)
_NUM = r"(\d+(?:[.,]\d+)?)"


def parse_report(text, reservoirs):
    """Extrae fecha, volumen, porcentaje y capacidad útil de cada reservorio pedido.

    ``reservoirs`` es ``{id: nombre en el reporte}``, p. ej. ``{"san_lorenzo": "San Lorenzo"}``.
    Devuelve una lista de diccionarios; lanza ``ValueError`` si no encuentra la fecha.
    """
    match = _FECHA.search(text)
    if not match or match.group(2).lower() not in _MESES:
        raise ValueError("Reporte SENAMHI sin fecha reconocible")
    day = pd.Timestamp(year=int(match.group(3)), month=_MESES[match.group(2).lower()],
                       day=int(match.group(1)))
    found = []
    for rid, name in reservoirs.items():
        line = re.search(rf"{re.escape(name)}\s+{_NUM}\s+{_NUM}\s+{_NUM}", text)
        if not line:
            continue
        volume, pct, capacity = (float(g.replace(",", ".")) for g in line.groups())
        found.append({"reservorio": rid, "date": day, "volumen": volume, "porcentaje": pct,
                      "capacidad_util": capacity})
    return found


def _text(content):
    from pypdf import PdfReader

    return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)


def _documents(settings):
    for url in settings.get("reportes", []):
        yield url, request("GET", url).content
    folder = Path(os.getenv("NORTEX_REPORTES_DIR", "data/local/reportes_senamhi"))
    if folder.is_dir():
        for path in sorted(folder.glob("*.pdf")):
            yield str(path), path.read_bytes()


def fetch(aoi, start, end, variables=None):
    """Volúmenes de los reservorios configurados (regional: igual para todos los AOI)."""
    selected = variables_for("senamhi_reportes", variables)
    if not selected:
        return frame()
    settings = config("sources")["senamhi_reportes"]
    catalog = config("variables")
    columns = {"reservoir_volume_report": "volumen", "reservoir_pct_report": "porcentaje",
               "reservoir_capacity_report": "capacidad_util"}
    rows, seen = [], set()
    for origin, content in _documents(settings):
        try:
            records = parse_report(_text(content), settings["reservorios"])
        except ValueError as error:
            _log.warning("%s: %s", origin, error)
            continue
        for record in records:
            key = (record["reservorio"], record["date"])
            if key in seen:
                continue
            seen.add(key)
            for variable in selected:
                rows.append(row(aoi, "senamhi_reportes", f'SENAMHI / {record["reservorio"]}',
                                variable, record["date"], record[columns[variable]],
                                catalog[variable]["unit"], "observado;pdf"))
    data = frame(rows)
    if start is not None:
        data = data[data.date >= pd.Timestamp(start)]
    if end is not None:
        data = data[data.date <= pd.Timestamp(end)]
    return data.reset_index(drop=True)
