from pathlib import Path

import pandas as pd

from nortex_data.derive.esi import anomaly, esi
from nortex_data.derive.et0 import daylight_seconds
from nortex_data.sources import power
from nortex_data.utils.appeears import AppEEARS, band_column
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years


def fetch(aoi, start, end, variables=None):
    """Consulta ECOSTRESS en fechas observadas y estima ESI si hace falta."""
    selected = variables_for("ecostress", variables)
    if not selected:
        return frame()
    settings = config("sources")["ecostress"]
    catalog = config("variables")
    client = AppEEARS(settings["endpoint"])
    client.authenticate()
    products = client.products()
    keys = set(selected)
    if keys & {"esi", "esi_anomaly"}:
        keys.update({"esi", "et_real"})
    start, end = bounds(settings["first"], start, end)
    rows = []
    for key in sorted(keys - {"esi_anomaly"}):
        entry = catalog[key]
        product = f'{entry["product"]}.{entry["version"]}'
        if product not in products:
            if key == "esi":
                continue
            raise RuntimeError(f"AppEEARS no ofrece {product}")
        data_layer = entry["api"]
        metadata = client.layers(product)
        if data_layer not in metadata:
            raise RuntimeError(f"ECOSTRESS: {data_layer} no existe en {product}")
        cloud = next((name for name in metadata if name.lower() == "cloud"), None)
        if not cloud:
            raise RuntimeError(f"ECOSTRESS: falta la capa cloud de {product}")
        layers = [{"product": product, "layer": name} for name in (data_layer, cloud)]
        for begin, stop in years(max(start, pd.Timestamp(entry["first"])), end):
            for table in client.point(aoi, begin, stop, layers):
                rows.extend(_observations(aoi, key, entry, product, table,
                                          metadata[data_layer].get("FillValue"),
                                          metadata[data_layer].get("Units")))
    return _complete(aoi, rows, selected)


_FLUX_UNITS = {"w/m^2", "w/m2", "w m-2", "wm-2", "w/m²", "w m^-2"}
_DEPTH_UNITS = {"mm/day", "mm/d", "mm day-1", "mm d-1", "mm"}


def _et_conversion(units):
    """Decide cómo pasar ETdaily a mm/día según la unidad declarada por AppEEARS.

    Devuelve ``("flux", flag)`` si llega como flujo medio diurno (W/m²) y hay que
    multiplicar por las horas de luz / λ; ``("depth", flag)`` si ya está en mm/día.
    Sin unidad declarada (CSV importados a mano) se asume flujo y se marca en ``qc_flag``.
    """
    if units is None or str(units).strip() == "":
        return "flux", "clear;units_assumed_w_m2"
    normalized = str(units).strip().lower()
    if normalized in _FLUX_UNITS:
        return "flux", "clear"
    if normalized in _DEPTH_UNITS:
        return "depth", "clear"
    raise ValueError(f"ECOSTRESS: unidad de ETdaily no reconocida: {units!r}")


def _observations(aoi, key, entry, product, table, fill=None, units=None):
    value_col, cloud_col = band_column(table, entry["api"]), band_column(table, "cloud")
    if not value_col or not cloud_col:
        raise RuntimeError(f"ECOSTRESS: CSV sin las capas pedidas de {product}")
    mode, flag = _et_conversion(units) if key == "et_real" else (None, "clear")
    clear = pd.to_numeric(table[cloud_col], errors="coerce").eq(0)
    for _, record in table.loc[clear].iterrows():
        value = pd.to_numeric(record[value_col], errors="coerce")
        if value == fill or pd.isna(value) or value in (-999, -9999):
            continue
        day = pd.Timestamp(record["Date"])
        if mode == "flux":
            value *= daylight_seconds(aoi["lat"], day.dayofyear) / 2.45e6
        yield row(aoi, "ecostress", product, key, day, value, entry["unit"], flag)


def import_point_csv(aoi, paths, variables=None):
    """Normaliza CSV de resultados puntuales exportados desde AppEEARS."""
    selected = variables_for("ecostress", variables)
    catalog = config("variables")
    rows = []
    found = set()
    for path in paths:
        normalized = Path(path).name.lower().replace(".", "-").replace("_", "-")
        for key in ("lst", "et_real", "esi"):
            entry = catalog[key]
            product = f'{entry["product"]}.{entry["version"]}'
            if product.lower().replace(".", "-").replace("_", "-") not in normalized:
                continue
            table = pd.read_csv(path)
            rows.extend(_observations(aoi, key, entry, product, table))
            found.add(key)
            break
    if not found:
        raise ValueError("No se encontraron CSV puntuales de los productos ECOSTRESS esperados")
    return _complete(aoi, rows, selected)


def _complete(aoi, rows, selected):
    result = frame(rows)
    if set(selected) & {"esi", "esi_anomaly"}:
        actual = result[result.variable == "et_real"].set_index("date").value
        index = result[result.variable == "esi"].set_index("date").value
        actual = actual.groupby(actual.index.normalize()).mean()
        index = index.groupby(index.index.normalize()).mean()
        missing = actual[~actual.index.isin(index.index)]
        if not missing.empty:
            reference = power.fetch(aoi, missing.index.min(), missing.index.max(), ["et0"])
            reference = reference.set_index("date").value.reindex(missing.index)
            estimates = esi(missing, reference).dropna()
            index = pd.concat([index, estimates]).sort_index()
            rows.extend(row(aoi, "ecostress", "ECOSTRESS JET / POWER", "esi", day, value,
                            "1", "derived_et0") for day, value in estimates.items())
        rows.extend(row(aoi, "ecostress", "ECOSTRESS ESI", "esi_anomaly", day, value,
                        "1", "derived") for day, value in anomaly(index).items())
    return frame(value for value in rows if value[6] in selected)
