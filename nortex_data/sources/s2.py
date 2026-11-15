import os
from datetime import datetime, timezone
from math import cos, radians

import pandas as pd
import requests
from dotenv import load_dotenv
from shapely.geometry import box, mapping, shape

from nortex_data.sources.s2_cog import fetch_public
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.http import credential, request

_PORTAL = "https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html"

_SCRIPT = """//VERSION=3
function setup() {
    return {input: ["B8A", "B05", "SCL", "dataMask"], output: [
        {id: "ndre", bands: 1, sampleType: "FLOAT32"},
        {id: "dataMask", bands: 1}
    ]}
}
function evaluatePixel(s) {
    const sum = s.B8A + s.B05
    const valid = s.dataMask && ![3, 8, 9, 10, 11].includes(s.SCL) && sum > 0
    return {ndre: [valid ? (s.B8A - s.B05) / sum : 0], dataMask: [+valid]}
}"""


def _geometry(aoi):
    if "geometry" in aoi:
        return aoi["geometry"]
    y = 20 / 111320
    x = y / max(cos(radians(aoi["lat"])), 0.01)
    return mapping(box(aoi["lon"] - x, aoi["lat"] - y, aoi["lon"] + x, aoi["lat"] + y))


def _local_dates(settings, aoi, start, end):
    params = {
        "collections": settings["product"],
        "bbox": ",".join(map(str, shape(_geometry(aoi)).bounds)),
        "datetime": f"{start:%Y-%m-%d}T00:00:00Z/{end:%Y-%m-%d}T23:59:59Z",
        "limit": 1,
        "fields": "id,properties.datetime,-geometry,-assets,-links",
    }
    dates = []
    for order in ("+datetime", "-datetime"):
        result = request("GET", settings["catalog"], params=dict(params, sortby=order)).json()
        if not result["features"]:
            return None
        timestamp = result["features"][0]["properties"]["datetime"]
        dates.append(pd.Timestamp(timestamp).tz_convert(None).normalize())
    return dates

def _payload(settings, aoi, begin, stop):
    until = min(stop + pd.Timedelta(days=1), pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None))
    return {
        "input": {
            "bounds": {
                "geometry": _geometry(aoi),
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            },
            "data": [{"type": settings["product"], "dataFilter": {"mosaickingOrder": "leastCC"}}],
        },
        "aggregation": {
            "timeRange": {"from": f"{begin:%Y-%m-%dT%H:%M:%SZ}", "to": f"{until:%Y-%m-%dT%H:%M:%SZ}"},
            "aggregationInterval": {"of": "P1D", "lastIntervalBehavior": "SKIP"},
            "resx": 20 / 111320 / max(cos(radians(aoi["lat"])), 0.01),
            "resy": 20 / 111320,
            "evalscript": _SCRIPT,
        },
        "calculations": {"ndre": {"statistics": {"default": {"percentiles": {"k": [10, 50, 90]}}}}},
    }


def fetch(aoi, start, end, variables=None):
    """Obtiene estadísticas NDRE diarias calculadas en CDSE."""
    selected = variables_for("s2", variables)
    if not selected:
        return frame()
    settings = config("sources")["s2"]
    catalog = config("variables")
    start, end = bounds(settings["first"], start, end)
    load_dotenv()
    if not (os.getenv("CDSE_CLIENT_ID") or os.getenv("CDSE_CLIENT_SECRET")):
        return fetch_public(aoi, shape(_geometry(aoi)), start, end, selected, settings, catalog)
    credentials = {
        "grant_type": "client_credentials",
        "client_id": credential("CDSE_CLIENT_ID", _PORTAL),
        "client_secret": credential("CDSE_CLIENT_SECRET", _PORTAL),
    }

    def authenticate():
        token = request("POST", settings["token"], data=credentials).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    local = _local_dates(settings, aoi, start, end) if start <= end else None
    if local is None:
        return frame()
    start, end = local
    headers = authenticate()
    rows = []
    for begin, stop in years(start, end):
        payload = _payload(settings, aoi, begin, stop)
        try:
            response = request("POST", settings["endpoint"], json=payload, headers=headers)
        except requests.HTTPError as error:
            if error.response.status_code != 401:
                raise
            headers = authenticate()
            response = request("POST", settings["endpoint"], json=payload, headers=headers)
        document = response.json()
        if document.get("status") not in {None, "OK"}:
            raise RuntimeError("CDSE no pudo calcular estadísticas NDRE")
        for record in document["data"]:
            if "error" in record:
                if record["error"].get("type") == "NO_DATA":
                    continue
                raise RuntimeError(f"Error de CDSE en {record['interval']}")
            day = pd.Timestamp(record["interval"]["from"]).tz_convert(None).normalize()
            stats = record["outputs"]["ndre"]["bands"]["B0"]["stats"]
            count = stats["sampleCount"] - stats["noDataCount"]
            values = dict(stats, validCount=count)
            for percentile, value in stats.get("percentiles", {}).items():
                values[str(int(float(percentile)))] = value
            for key in selected:
                entry = catalog[key]
                value = values.get(entry["api"]) if count or key == "ndre_count" else None
                rows.append(row(aoi, "s2", settings["product"], key, day, value,
                                entry["unit"], "ok" if count else "no_valid_pixels"))
    return frame(rows)
