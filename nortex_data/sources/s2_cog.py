from collections import defaultdict

import numpy as np
import pandas as pd

from nortex_data.utils.core import frame, row, years
from nortex_data.utils.http import request

_ASSETS = ("nir08", "rededge1", "scl")
_EXCLUDED = (0, 1, 3, 8, 9, 10, 11)


def _items(settings, geometry, start, end):
    url = settings["public_catalog"]
    params = {
        "bbox": ",".join(map(str, geometry.bounds)),
        "datetime": f"{start:%Y-%m-%d}T00:00:00Z/{end:%Y-%m-%d}T23:59:59Z",
        "limit": 100,
    }
    visited = set()
    while url:
        response = request("GET", url, params=params)
        if response.url in visited:
            raise RuntimeError("Sentinel-2: el catálogo repitió una página")
        visited.add(response.url)
        document = response.json()
        yield from document["features"]
        url = next((link["href"] for link in document["links"] if link["rel"] == "next"), None)
        params = None


def _reflectance(values, asset, properties):
    band = asset["raster:bands"][0]
    offset = 0 if properties.get("earthsearch:boa_offset_applied") else band["offset"]
    return values.astype("float64") * band["scale"] + offset


def _values(item, geometry):
    import rasterio
    from rasterio.errors import WindowError
    from rasterio.features import geometry_mask, geometry_window
    from rasterio.warp import transform_geom

    assets = [item["assets"][key] for key in _ASSETS]
    values = []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        for index, asset in enumerate(assets):
            url = asset["href"]
            with request("GET", url, headers={"Range": "bytes=0-0"}, stream=True) as response:
                if response.status_code != 206:
                    raise RuntimeError("Sentinel-2: el activo no respondió con rango HTTP")
            with rasterio.open(f"/vsicurl/{url}") as dataset:
                if index == 0:
                    projected = transform_geom("EPSG:4326", dataset.crs, geometry.__geo_interface__)
                    try:
                        window = geometry_window(dataset, [projected])
                    except WindowError:
                        return np.array([])
                    if window.width * window.height > 2_000_000:
                        raise ValueError("Sentinel-2: la ventana supera el máximo para un AOI")
                    grid = dataset.transform, dataset.crs, dataset.shape
                    inside = geometry_mask([projected], transform=dataset.window_transform(window),
                                           out_shape=(int(window.height), int(window.width)), invert=True)
                elif grid != (dataset.transform, dataset.crs, dataset.shape):
                    raise RuntimeError("Sentinel-2: B8A, B05 y SCL tienen cuadrículas distintas")
                values.append(dataset.read(1, window=window, masked=True))
    nir, red, scl = values
    nir_data = _reflectance(nir.data, assets[0], item["properties"])
    red_data = _reflectance(red.data, assets[1], item["properties"])
    valid = inside & ~np.ma.getmaskarray(nir) & ~np.ma.getmaskarray(red) & ~np.ma.getmaskarray(scl)
    valid &= ~np.isin(scl.data, _EXCLUDED) & (nir_data + red_data > 0)
    return (nir_data[valid] - red_data[valid]) / (nir_data[valid] + red_data[valid])


def fetch_public(aoi, geometry, start, end, selected, settings, catalog):
    """Calcula NDRE leyendo por HTTP únicamente las ventanas COG del AOI."""
    rows = []
    for begin, stop in years(start, end):
        days = defaultdict(list)
        for item in _items(settings, geometry, begin, stop):
            day = pd.Timestamp(item["properties"]["datetime"]).tz_convert(None).normalize()
            days[day].append(item)
        for day, items in days.items():
            samples = max((_values(item, geometry) for item in items), key=len)
            values = {"validCount": len(samples)}
            if len(samples):
                p10, median, p90 = np.percentile(samples, [10, 50, 90])
                values.update(mean=samples.mean(), stDev=samples.std(), **{"10": p10, "50": median, "90": p90})
            for key in selected:
                entry = catalog[key]
                flag = "cog_window" if len(samples) else "cog_no_valid_pixels"
                rows.append(row(aoi, "s2", "sentinel-2-l2a / Earth Search COG",
                                key, day, values.get(entry["api"]), entry["unit"], flag))
    return frame(rows)
