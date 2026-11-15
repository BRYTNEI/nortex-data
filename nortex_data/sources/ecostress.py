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
                value_col, cloud_col = band_column(table, data_layer), band_column(table, cloud)
                if not value_col or not cloud_col:
                    raise RuntimeError(f"ECOSTRESS: CSV sin las capas pedidas de {product}")
                clear = pd.to_numeric(table[cloud_col], errors="coerce").eq(0)
                for _, record in table.loc[clear].iterrows():
                    value = record[value_col]
                    fill = metadata[data_layer].get("FillValue")
                    if value == fill or pd.isna(value) or value in (-999, -9999):
                        continue
                    day = pd.Timestamp(record["Date"])
                    if key == "et_real":
                        value *= daylight_seconds(aoi["lat"], day.dayofyear) / 2.45e6
                    rows.append(row(aoi, "ecostress", product, key, day,
                                    value, entry["unit"], "clear"))
    result = frame(rows)
    if keys & {"esi", "esi_anomaly"}:
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
