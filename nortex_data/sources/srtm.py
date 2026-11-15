"""Relieve SRTM 30 m (altitud, pendiente y desnivel) vía la API pública de OpenTopoData.

Uso en la v0.7: altitud del sitio para ET0 (§9.1), drenaje y riesgo de encharcamiento en
años El Niño (RT-05, §10.3.1). Solo viajan las cotas de los puntos pedidos.

- Punto: malla 3 × 3 a 30 m alrededor; pendiente por el método de Horn.
- Polígono: hasta ``max_points`` cotas dentro del polígono (altitud media y desnivel) y la
  pendiente en su punto representativo.
Las propiedades son estáticas: ``date`` queda vacío. Límite del servicio: 100 ubicaciones por
petición y 1 petición por segundo.
"""

import math
import time

import numpy as np
import pandas as pd
from shapely.geometry import Point, shape

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import request

_SPACING_M = 30.0


def _elevations(settings, points):
    values = []
    for start in range(0, len(points), 100):
        chunk = points[start:start + 100]
        locations = "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in chunk)
        document = request("GET", settings["endpoint"], params={"locations": locations}).json()
        if document.get("status") != "OK":
            raise RuntimeError(f"SRTM: {document.get('error', 'respuesta inválida')}")
        values.extend(item["elevation"] for item in document["results"])
        time.sleep(settings.get("pause_s", 1.0))
    return np.array([np.nan if v is None else float(v) for v in values])


def horn_slope(grid, spacing_m=_SPACING_M):
    """Pendiente (%) en el centro de una malla 3 × 3 de cotas (método de Horn)."""
    z = np.asarray(grid, dtype="float64").reshape(3, 3)
    dzdx = ((z[0, 2] + 2 * z[1, 2] + z[2, 2]) - (z[0, 0] + 2 * z[1, 0] + z[2, 0])) / (8 * spacing_m)
    dzdy = ((z[2, 0] + 2 * z[2, 1] + z[2, 2]) - (z[0, 0] + 2 * z[0, 1] + z[0, 2])) / (8 * spacing_m)
    return float(math.hypot(dzdx, dzdy) * 100)


def _neighbourhood(lat, lon):
    dlat = _SPACING_M / 111_320
    dlon = dlat / max(math.cos(math.radians(lat)), 0.01)
    return [(lat + i * dlat, lon + j * dlon) for i in (1, 0, -1) for j in (-1, 0, 1)]


def _polygon_points(geometry, max_points):
    polygon = shape(geometry)
    west, south, east, north = polygon.bounds
    n = max(2, int(math.sqrt(max_points)))
    points = [(y, x) for y in np.linspace(south, north, n) for x in np.linspace(west, east, n)
              if polygon.contains(Point(x, y))]
    return points or [(polygon.representative_point().y, polygon.representative_point().x)]


def fetch(aoi, start, end, variables=None):
    """Altitud, pendiente y desnivel del AOI."""
    selected = variables_for("srtm", variables)
    if not selected:
        return frame()
    settings = config("sources")["srtm"]
    catalog = config("variables")
    grid = _elevations(settings, _neighbourhood(aoi["lat"], aoi["lon"]))
    values = {"slope": horn_slope(grid), "elevation": float(grid[4]),
              "relief": float(np.nanmax(grid) - np.nanmin(grid))}
    flag = "point_3x3"
    if "geometry" in aoi:
        cotas = _elevations(settings, _polygon_points(aoi["geometry"], settings["max_points"]))
        values["elevation"] = float(np.nanmean(cotas))
        values["relief"] = float(np.nanmax(cotas) - np.nanmin(cotas))
        flag = f"polygon_{len(cotas)}_points"
    return frame(
        row(aoi, "srtm", catalog[key]["product"], key, pd.NaT, values[key], catalog[key]["unit"], flag)
        for key in selected
    )
