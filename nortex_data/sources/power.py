import re

import numpy as np
import pandas as pd
import requests

from nortex_data.derive.et0 import et0, saturation_vapor_pressure
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.http import request


def _point(settings, aoi, start, end, codes):
    params = {
        "community": "AG", "format": "JSON", "time-standard": "LST",
        "latitude": aoi["lat"], "longitude": aoi["lon"],
        "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"),
        "parameters": ",".join(codes),
    }
    if "elevation_m" in aoi:
        params["site-elevation"] = aoi["elevation_m"]
    try:
        return request("GET", settings["endpoint"], params=params).json()
    except requests.HTTPError as error:
        if error.response.status_code != 422:
            raise
        # POWER indica el término del registro cuando se consulta hasta hoy.
        message = " ".join(error.response.json().get("messages", []))
        dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", message)
        if len(dates) < 2 or "date" not in message.lower():
            raise
        latest = max(pd.Timestamp(day) for day in dates)
        if latest < start:
            return None
        if latest >= end:
            raise
        return _point(settings, aoi, start, latest, codes)


def _series(payload, entries):
    reported = payload["parameters"]
    fill = payload["header"]["fill_value"]
    data = payload["properties"]["parameter"]
    values = {}
    for key, entry in entries.items():
        code = entry["api"].split("/")[0]
        if key == "pressure" and "PSC" in data:
            code = "PSC"
        unit = reported[code]["units"]
        series = pd.Series(data[code], dtype=float).replace([fill, -999, -9999], np.nan)
        if key == "solar" and unit in {"kW-hr/m^2/day", "kWh/m^2/day"}:
            series *= 3.6
        elif unit.lower() != entry["unit"].lower():
            raise ValueError(f"POWER: unidad inesperada para {code}: {unit}")
        values[key] = series
    result = pd.DataFrame(values)
    result.index = pd.to_datetime(result.index, format="%Y%m%d")
    return result


def fetch(aoi, start, end, variables=None):
    """Obtiene series diarias POWER para el punto de referencia del AOI."""
    settings = config("sources")["power"]
    catalog = config("variables")
    selected = variables_for("power", variables)
    if not selected:
        return frame()
    keys = dict.fromkeys(selected)
    if "et0" in keys:
        keys.update(dict.fromkeys(catalog["et0"]["inputs"]))
    entries = {key: catalog[key] for key in keys if catalog[key]["api"]}
    start, end = bounds(settings["first"], start, end)
    rows = []
    for begin, stop in years(start, end):
        payload = _point(settings, aoi, begin, stop, [entry["api"].split("/")[0] for entry in entries.values()])
        if payload is None:
            continue
        data = _series(payload, entries)
        elevation = aoi["elevation_m"] if "elevation_m" in aoi else payload["geometry"]["coordinates"][2]
        if "et0" in selected:
            vapor = saturation_vapor_pressure(data.dewpoint).fillna(
                (saturation_vapor_pressure(data.tmax) + saturation_vapor_pressure(data.tmin))
                / 2 * data.rh2m / 100
            )
            data["et0"] = et0(data.tmax, data.tmin, data.solar, data.wind2m, vapor,
                             aoi["lat"], elevation, data.index.dayofyear, data.pressure)
        for key in selected:
            series = data.loc[data.index >= pd.Timestamp(catalog[key]["first"]), key]
            last = series.last_valid_index()
            if last is not None:
                for day, value in series.loc[:last].items():
                    rows.append(row(aoi, "power", settings["product"], key, day,
                                    value, catalog[key]["unit"], "derived" if key == "et0" else "ok"))
    return frame(rows)
