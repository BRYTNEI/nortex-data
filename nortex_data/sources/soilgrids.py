"""Propiedades del suelo de SoilGrids 2.0 (ISRIC, 250 m) por WCS.

Respaldo cuando no hay análisis de laboratorio (EX-03: «dato global»). Se pide al servidor
una ventana mínima alrededor del AOI (``window_deg``) con ``GetCoverage``: viajan unos cientos
de bytes por propiedad y profundidad. SoilGrids enmascara zonas sin predicción (urbanas,
agua, suelo desnudo): se toma el píxel válido más cercano y se registra la distancia.

La API REST de SoilGrids estuvo caída (HTTP 503) en la verificación del 15/11/2026; el WCS
respondió. Las propiedades son estáticas: ``date`` queda vacío.
"""

import math

import numpy as np
import pandas as pd

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import request


def _window(settings, prop, depth, aoi):
    d = settings["window_deg"]
    params = [
        ("map", f"/map/{prop}.map"), ("SERVICE", "WCS"), ("VERSION", "2.0.1"),
        ("REQUEST", "GetCoverage"), ("COVERAGEID", f"{prop}_{depth}_mean"),
        ("FORMAT", "image/tiff"),
        ("SUBSET", f"long({aoi['lon'] - d},{aoi['lon'] + d})"),
        ("SUBSET", f"lat({aoi['lat'] - d},{aoi['lat'] + d})"),
        ("SUBSETTINGCRS", "http://www.opengis.net/def/crs/EPSG/0/4326"),
        ("OUTPUTCRS", "http://www.opengis.net/def/crs/EPSG/0/4326"),
    ]
    response = request("GET", settings["endpoint"], params=params)
    if not response.content.startswith((b"II*\x00", b"MM\x00*")):
        raise RuntimeError(f"SoilGrids: el WCS no devolvió un GeoTIFF para {prop} {depth}")
    return response.content


def nearest_valid(content, lat, lon, nodata=0):
    """Valor del píxel válido más cercano al punto y su distancia en metros."""
    from rasterio.io import MemoryFile

    with MemoryFile(content) as memory, memory.open() as dataset:
        data = dataset.read(1).astype("float64")
        rows, cols = np.indices(data.shape)
        t = dataset.transform  # malla norte-arriba sin rotación (EPSG:4326)
        xs = t.c + (cols + 0.5) * t.a
        ys = t.f + (rows + 0.5) * t.e
    valid = (data != nodata) & np.isfinite(data)
    if not valid.any():
        return None, None
    dy = (ys - lat) * 111_320
    dx = (xs - lon) * 111_320 * math.cos(math.radians(lat))
    distance = np.hypot(dx, dy)
    distance[~valid] = np.inf
    index = np.unravel_index(int(distance.argmin()), distance.shape)
    return float(data[index]), float(distance[index])


def fetch(aoi, start, end, variables=None):
    """Propiedades por profundidad en el punto representativo del AOI."""
    selected = variables_for("soilgrids", variables)
    if not selected:
        return frame()
    settings = config("sources")["soilgrids"]
    catalog = config("variables")
    rows = []
    for key in selected:
        entry = catalog[key]
        for depth in settings["depths"]:
            content = _window(settings, entry["api"], depth, aoi)
            value, distance = nearest_valid(content, aoi["lat"], aoi["lon"])
            if value is not None:
                value = value / entry["factor"]
                flag = f"global_250m;nearest_m={distance:.0f}"
            else:
                flag = "global_250m;no_valid_pixel"
            rows.append(row(aoi, "soilgrids", f"SoilGrids 2.0 / {depth}", key, pd.NaT,
                            value, entry["unit"], flag))
    return frame(rows)
