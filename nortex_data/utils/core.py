from datetime import date
from importlib.resources import files
from pathlib import Path

import pandas as pd
import yaml
from shapely.geometry import shape

COLUMNS = "date aoi_id lat lon source product variable value unit qc_flag".split()
SOURCES = ("power", "imerg", "smap", "ecostress", "s2",)


def config(name):
    """Lee la configuración local o los valores incluidos en el paquete."""
    local = Path("config") / f"{name}.yaml"
    path = local if local.is_file() else files("nortex_data").joinpath("_config", local.name)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_aois(path=None):
    """Valida puntos y polígonos GeoJSON pequeños en WGS84."""
    entries = config("aois") if path is None else yaml.safe_load(
        Path(path).read_text(encoding="utf-8")
    )
    result = {}
    for aoi_id, values in entries["aois"].items():
        aoi = dict(values, aoi_id=aoi_id)
        if "geometry" in aoi:
            geometry = shape(aoi["geometry"])
            if geometry.geom_type not in {"Polygon", "MultiPolygon"} or not geometry.is_valid:
                raise ValueError(f"{aoi_id}: polígono GeoJSON inválido")
            west, south, east, north = geometry.bounds
            if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
                raise ValueError(f"{aoi_id}: coordenadas fuera de WGS84")
            if east - west > 0.25 or north - south > 0.25:
                raise ValueError(f"{aoi_id}: el polígono excede 0.25° por eje")
            point = geometry.representative_point()
            aoi.update(lat=point.y, lon=point.x)
        if not (-90 <= aoi["lat"] <= 90 and -180 <= aoi["lon"] <= 180):
            raise ValueError(f"{aoi_id}: coordenadas fuera de WGS84")
        result[aoi_id] = aoi
    return result


def bounds(first, start=None, end=None):
    """Acota el intervalo solicitado al registro y a diez años móviles."""
    today = pd.Timestamp(date.today())
    lower = max(pd.Timestamp(first), today - pd.DateOffset(years=10))
    upper = today if end is None else min(today, pd.Timestamp(end).normalize())
    if start is not None:
        lower = max(lower, pd.Timestamp(start).normalize())
    return lower, upper


def years(start, end):
    """Divide un intervalo inclusivo por años calendario."""
    while start <= end:
        stop = min(end, start.replace(month=12, day=31))
        yield start, stop
        start = stop + pd.Timedelta(days=1)


def row(aoi, source, product, variable, day, value, unit, flag="ok"):
    """Construye una observación y normaliza valores de relleno."""
    value = pd.to_numeric(value, errors="coerce")
    if pd.isna(value) or value in (-999, -9999, float("inf"), -float("inf")):
        value = float("nan")
        flag = "missing" if flag == "ok" else f"{flag};missing"
    return (day, aoi["aoi_id"], aoi["lat"], aoi["lon"], source, product,
            variable, value, unit, flag)


def frame(rows=()):
    """Devuelve observaciones en el esquema común y en orden estable."""
    result = pd.DataFrame(rows, columns=COLUMNS)
    result["date"] = pd.to_datetime(result["date"])
    result["value"] = pd.to_numeric(result["value"])
    return result.sort_values(["date", "aoi_id", "source", "variable"], ignore_index=True)


def variables_for(source, requested=None):
    """Selecciona únicamente los identificadores declarados para la fuente."""
    catalog = config("variables")
    ids = [key for key, entry in catalog.items() if entry["source"] == source]
    if requested is None:
        return ids
    unknown = set(requested) - set(ids)
    if unknown:
        raise ValueError(f"{source}: variables desconocidas: {', '.join(sorted(unknown))}")
    return list(dict.fromkeys(requested))
