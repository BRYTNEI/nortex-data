import os

import pandas as pd
from dotenv import load_dotenv

from nortex_data.utils.appeears import AppEEARS, band_column
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.public_zarr import daily_point


def fetch(aoi, start, end, variables=None):
    """Obtiene humedad SMAP y agrega las observaciones de tres horas a diario."""
    selected = variables_for("smap", variables)
    if not selected:
        return frame()
    settings = config("sources")["smap"]
    catalog = config("variables")
    load_dotenv()
    start, end = bounds(settings["first"], start, end)
    if not os.getenv("APPEEARS_TOKEN") and not (
        os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD")
    ):
        codes = {key: settings["public_bands"][key] for key in selected}
        data = daily_point(settings["public_zarr"], aoi, start, end, list(codes.values()))
        return frame(
            row(aoi, "smap", "SMAP L4 / NASA POWER", key, day, value, catalog[key]["unit"],
                "daily_utc;qc_unavailable")
            for key, code in codes.items() for day, value in data[code].items()
        )
    client = AppEEARS(settings["endpoint"])
    client.authenticate()
    product = f'{settings["product"]}.{settings["version"]}'
    products = client.products()
    if product not in products:
        raise RuntimeError(f"AppEEARS no ofrece {product}; revisa el catálogo de SMAP y Harmony.")
    metadata = client.layers(product)
    codes = {key: catalog[key]["api"] for key in selected}
    if not set(codes.values()) <= set(metadata):
        raise RuntimeError(f"SMAP: capas configuradas ausentes en {product}")
    quality = [name for name in metadata if "quality_flag" in name.lower()]
    layers = [{"product": product, "layer": name} for name in [*codes.values(), *quality]]
    rows = []
    for begin, stop in years(start, end):
        for table in client.point(aoi, begin, stop, layers):
            days = pd.to_datetime(table["Date"], utc=True).dt.tz_convert(None).dt.normalize()
            for key, code in codes.items():
                column = band_column(table, code)
                if column is None:
                    continue
                vals = pd.to_numeric(table[column], errors="coerce")
                vals = vals.replace([-9999, -999, metadata[code].get("FillValue")], float("nan"))
                daily = vals.groupby(days).agg(["mean", "count"])
                flags = {}
                for name in quality:
                    qc_col = band_column(table, name)
                    if qc_col is not None:
                        flags[name] = table[qc_col].groupby(days).agg(
                            lambda values: "|".join(sorted(set(values.dropna().astype(str))))
                        )
                for day, values in daily.iterrows():
                    flag = f'samples={int(values["count"])}' if quality else f'samples={int(values["count"])};qc_unavailable'
                    for name, observed in flags.items():
                        flag += f";{name}={observed.loc[day]}"
                    rows.append(row(aoi, "smap", product, key, day, values["mean"],
                                    catalog[key]["unit"], flag))
    return frame(rows)
