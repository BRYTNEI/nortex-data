import math
import re
from urllib.parse import urlparse

import pandas as pd

from nortex_data.derive.extremos import extremos
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.http import credential, request

_NUMBER = r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][-+]?\d+)?"


def _granules(settings, product, aoi, begin, stop):
    params = {
        "short_name": product, "version": settings["version"],
        "temporal": f"{begin:%Y-%m-%d}T00:00:00Z,{stop:%Y-%m-%d}T23:59:59Z",
        "point": f'{aoi["lon"]},{aoi["lat"]}', "page_size": 500,
    }
    response = request("GET", settings["endpoint"], params=params)
    for item in response.json()["items"]:
        granule = item["umm"]
        interval = granule["TemporalExtent"]["RangeDateTime"]
        day = pd.Timestamp(interval["BeginningDateTime"]).tz_convert(None).normalize()
        if not begin <= day <= stop:
            continue
        for related in granule.get("RelatedUrls", []):
            url = related["URL"]
            parsed = urlparse(url)
            if parsed.scheme == "https" and parsed.hostname and (
                parsed.hostname.endswith(".nasa.gov") and related.get("Subtype") == "OPENDAP DATA"
            ):
                yield day, parsed._replace(query="", fragment="").geturl().removesuffix(".html")
                break
        else:
            raise RuntimeError(f"{product} {day.date()}: CMR no entregó un enlace OPeNDAP")


def _pixel(url, aoi, headers, variable):
    lon = min(3599, math.floor((aoi["lon"] + 180) * 10))
    lat = min(1799, math.floor((aoi["lat"] + 90) * 10))
    expression = f"{variable}[0:1:0][{lon}:1:{lon}][{lat}:1:{lat}]"
    response = request("GET", f"{url}.ascii?{expression}", headers=headers, stream=True)
    with response:
        payload = response.raw.read(16385, decode_content=True)
    if len(payload) > 16384:
        raise RuntimeError("IMERG: respuesta OPeNDAP fuera del límite para un píxel")
    _, separator, data = payload.decode("ascii").partition("---------------------------------------------")
    values = re.findall(rf"(?m)^\[0\]\[0\](?:\[0\])?,\s*({_NUMBER})\s*$", data)
    if not separator or len(values) != 1:
        raise ValueError("IMERG: no se pudo interpretar el píxel OPeNDAP")
    value = float(values[0])
    return value if value >= 0 else float("nan")


def fetch(aoi, start, end, variables=None):
    """Lee un píxel diario por OPeNDAP, priorizando Final sobre Late."""
    selected = variables_for("imerg", variables)
    if not selected:
        return frame()
    token = credential("EARTHDATA_TOKEN", "https://urs.earthdata.nasa.gov/")
    headers = {"Authorization": f"Bearer {token}"}
    settings = config("sources")["imerg"]
    catalog = config("variables")
    start, end = bounds(settings["first"], start, end)
    records = {}
    for begin, stop in years(start, end):
        final = dict(_granules(settings, settings["product"], aoi, begin, stop))
        late_start = max(final, default=begin - pd.Timedelta(days=1)) + pd.Timedelta(days=1)
        late = dict(_granules(settings, settings["late"], aoi, late_start, stop)) if late_start <= stop else {}
        for product, flag, granules in [
            (settings["product"], "final", final), (settings["late"], "late", late)
        ]:
            for day, url in granules.items():
                value = _pixel(url, aoi, headers, catalog["precipitation"]["api"])
                records[day] = row(aoi, "imerg", product, "precipitation", day, value, "mm/day", flag)
    data = frame(records.values())
    if data.empty:
        return data
    precipitation = data.set_index("date")["value"]
    summary, monthly = extremos(precipitation)
    flag = "derived_includes_late" if data.qc_flag.str.startswith("late").any() else "derived_final"
    derived = [
        row(aoi, "imerg", settings["product"], key, data.date.max(), value, catalog[key]["unit"], flag)
        for key, value in summary.items() if key in selected
    ]
    if "monthly_precip" in selected:
        derived.extend(
            row(aoi, "imerg", settings["product"], "monthly_precip", day, value, "mm", flag)
            for day, value in monthly.items()
        )
    if "precipitation" in selected:
        derived.extend(records.values())
    return frame(derived)
