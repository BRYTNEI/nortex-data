import json

import pandas as pd

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import request


def _arcgis(url, **params):
    result = request("GET", url, params=dict(params, f="json")).json()
    if "error" in result:
        raise RuntimeError(f'GAEZ: {result["error"]["message"]}')
    return result


def _quote(value):
    return "'" + value.replace("'", "''") + "'"


def _catalog(settings, crop):
    service = settings["endpoint"] + "/res05/ImageServer"
    filters = {
        "crop": crop, "variable": settings["variable"], "input_level": settings["input_level"],
        "water_supply": settings["water_supply"],
    }
    fields = "objectid,crop,year,model,rcp,input_level,water_supply,c02_fertilization,units"
    where = " AND ".join(f"{key}={_quote(value)}" for key, value in filters.items())
    data = _arcgis(f"{service}/query", where=where, outFields=fields, returnGeometry="false")
    if data.get("exceededTransferLimit"):
        raise RuntimeError("GAEZ: reduce el filtro de cultivos o escenarios")
    for feature in data["features"]:
        yield feature["attributes"], service


def _sample(service, aoi, layer):
    point = json.dumps({"x": aoi["lon"], "y": aoi["lat"], "spatialReference": {"wkid": 4326}})
    mosaic = json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [layer]})
    result = _arcgis(f"{service}/identify", geometry=point, geometryType="esriGeometryPoint",
                     mosaicRule=mosaic, returnCatalogItems="false", returnGeometry="false")
    return result.get("value")


def _range_sample(url, aoi):
    import rasterio
    from rasterio.warp import transform

    if not url.startswith("https://"):
        raise ValueError("GAEZ: la capa debe especificar una URL HTTPS de un COG")
    response = request("GET", url, headers={"Range": "bytes=0-0"}, stream=True)
    with response:
        if response.status_code != 206 or not response.headers.get("Content-Range", "").startswith("bytes 0-0/"):
            raise ValueError("GAEZ: el servidor debe admitir lectura por rango")
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_USE_HEAD="YES"):
        with rasterio.open(f"/vsicurl/{url}") as dataset:
            x, y = transform("EPSG:4326", dataset.crs, [aoi["lon"]], [aoi["lat"]])
            sample = next(dataset.sample(zip(x, y), indexes=1, masked=True))
            return sample.filled(0)[0] if not sample.mask.any() else None


def fetch(aoi, start, end, variables=None):
    """Muestrea las capas climáticas GAEZ por cultivo, escenario y periodo."""
    if not variables_for("gaez", variables):
        return frame()
    settings = config("sources")["gaez"]
    rows = []
    if str(settings["version"]) == "4":
        for crop in settings["crops"]:
            for layer, service in _catalog(settings, crop):
                value = _sample(service, aoi, layer["objectid"])
                product = f'GAEZ v4 / {crop} / {layer["year"]} / {layer["model"]} / {layer["rcp"]} / {layer["c02_fertilization"]}'
                flag = f'{layer["input_level"]};{layer["water_supply"]}'
                rows.append(row(aoi, "gaez", product, "suitability", pd.NaT, value, layer["units"], flag))
    for layer in settings["layers"]:
        if str(layer["version"]) == str(settings["version"]):
            value = _range_sample(layer["url"], aoi)
            product = f'GAEZ v{layer["version"]} / {layer["crop"]} / {layer["period"]} / {layer["scenario"]}'
            rows.append(row(aoi, "gaez", product, "suitability", pd.NaT, value, layer["unit"], layer["input"]))
    if not rows:
        raise RuntimeError("GAEZ: sin capas coincidentes. Revisa los filtros o configura capas COG en sources.yaml.")
    return frame(rows)
