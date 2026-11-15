"""NASA POWER horario: temperatura y humedad para vigilar condiciones de antracnosis (V-41).

Además de las series horarias, deriva por día:
- ``hours_rh90``: horas con HR ≥ 90 %.
- ``hours_wet_warm``: horas con HR ≥ 90 % y 20 °C ≤ T ≤ 30 °C.
Los umbrales son de literatura fitopatológica general y están **POR VALIDAR**; la salida se
interpreta como «condiciones favorables», nunca como probabilidad de infección (v0.7 §4.3 de
la auditoría). Celda regional de POWER (~50 km): no representa el microclima del huerto.
"""

import pandas as pd

from nortex_data.utils.blocks import cached_block, concat_blocks
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.http import request

_RAW = {"t2m_hourly": "T2M", "rh2m_hourly": "RH2M"}


def hourly_rows(payload, aoi, selected, catalog, product):
    """Convierte la respuesta horaria de POWER en filas horarias y conteos diarios."""
    data = payload["properties"]["parameter"]
    fill = payload["header"]["fill_value"]
    units = {k: v["units"] for k, v in payload["parameters"].items()}
    if units.get("T2M") != "C" or units.get("RH2M") != "%":
        raise ValueError(f"POWER horario: unidades inesperadas {units}")
    frame_ = pd.DataFrame({k: pd.Series(v, dtype=float) for k, v in data.items()})
    frame_.index = pd.to_datetime(frame_.index, format="%Y%m%d%H")
    frame_ = frame_.mask(frame_.isin([fill, -999, -9999]))
    rows = []
    for key, code in _RAW.items():
        if key in selected:
            rows.extend(row(aoi, "power_horario", product, key, ts, v, catalog[key]["unit"])
                        for ts, v in frame_[code].items())
    wet = frame_["RH2M"].ge(90)
    warm = frame_["T2M"].between(20, 30)
    complete = frame_[["T2M", "RH2M"]].notna().all(axis=1).groupby(frame_.index.normalize()).sum()
    for key, mask in (("hours_rh90", wet), ("hours_wet_warm", wet & warm)):
        if key not in selected:
            continue
        counts = mask.groupby(frame_.index.normalize()).sum()
        for day, value in counts.items():
            ok = complete.loc[day] == 24
            rows.append(row(aoi, "power_horario", product, key, day, value if ok else None,
                            catalog[key]["unit"], "derived" if ok else "derived;incomplete_day"))
    return frame(rows)


def fetch(aoi, start, end, variables=None):
    """Series horarias y conteos diarios (regla de 10 años, bloques anuales)."""
    selected = variables_for("power_horario", variables)
    if not selected:
        return frame()
    settings = config("sources")["power_horario"]
    catalog = config("variables")
    start, end = bounds(settings["first"], start, end)

    def block(begin, stop):
        params = {
            "parameters": "T2M,RH2M", "community": "AG", "format": "JSON",
            "time-standard": "LST", "latitude": aoi["lat"], "longitude": aoi["lon"],
            "start": f"{begin:%Y%m%d}", "end": f"{stop:%Y%m%d}",
        }
        payload = request("GET", settings["endpoint"], params=params).json()
        return hourly_rows(payload, aoi, selected, catalog, settings["product"])

    data = concat_blocks(
        cached_block("power_horario", aoi, begin, stop, [sorted(selected)], block)
        for begin, stop in years(start, end)
    )
    if data.empty:
        return data
    # POWER publica con rezago: se recortan las horas finales sin dato.
    last = data.loc[data.value.notna(), "date"].max()
    return data[data.date <= last].reset_index(drop=True)
