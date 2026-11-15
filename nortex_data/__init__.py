import hashlib
import json
import logging
import os
from importlib import import_module
from pathlib import Path
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv

from nortex_data.utils.core import SOURCES, bounds, config, frame, load_aois

__all__ = ["get_dataset"]


def _fetch(source, aoi, start, end, variables):
    settings = config("sources")[source]
    catalog = config("variables")
    if source == "faostat":
        return import_module("nortex_data.sources.faostat").fetch(aoi, start, end, variables)
    begin, stop = bounds(settings["first"], start, end)
    inputs = [source, aoi, str(begin.date()), str(stop.date()), settings, catalog, variables]
    digest = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    path = Path("cache") / f"{source}-{digest}.parquet"
    load_dotenv()
    # Las consultas abiertas se repiten para incorporar nuevas publicaciones.
    cache = os.getenv("NORTEX_CACHE") != "0" and stop < bounds(settings["first"])[1] - pd.Timedelta(days=365)
    if cache and path.is_file():
        return pd.read_parquet(path)
    logging.getLogger(__name__).info("Consultando %s para %s", source, aoi["aoi_id"])
    provider = import_module(f"nortex_data.sources.{source}")
    result = provider.fetch(aoi, begin, stop, variables)
    if cache and not result.empty:
        path.parent.mkdir(exist_ok=True)
        temporary = path.with_name(f"{path.stem}-{uuid4().hex}.tmp")
        try:
            result.to_parquet(temporary, index=False)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    return result


def get_dataset(source=None, aoi_id=None, start=None, end=None, *, variables=None, aoi_path=None):
    """Obtiene observaciones por fuente o por identificadores internos de variables."""
    aois = load_aois(aoi_path)
    if aoi_id not in aois:
        raise ValueError(f"AOI no configurado: {aoi_id}. Opciones: {', '.join(aois)}")
    if source not in (*SOURCES, "all", None):
        raise ValueError(f"Fuente desconocida: {source}")
    catalog = config("variables")
    groups = {}
    if variables is not None:
        ids = [variables] if isinstance(variables, str) else variables
        for key in ids:
            if key not in catalog:
                raise ValueError(f"Variable desconocida: {key}")
            owner = catalog[key]["source"]
            if source not in (None, "all", owner):
                raise ValueError(f"{key} pertenece a {owner}, no a {source}")
            groups.setdefault(owner, []).append(key)
    elif source == "all":
        groups = dict.fromkeys(SOURCES)
    elif source:
        groups[source] = None
    else:
        raise ValueError("Indica source o variables")
    outputs = []
    errors = {}
    for owner, ids in groups.items():
        try:
            outputs.append(_fetch(owner, aois[aoi_id], start, end, ids))
        except Exception as error:
            if len(groups) == 1:
                raise
            errors[owner] = str(error)
            logging.getLogger(__name__).error("%s: %s", owner, error)
    result = frame() if not outputs else pd.concat(outputs, ignore_index=True).sort_values(
        ["date", "aoi_id", "source", "variable"], ignore_index=True
    )
    result.attrs["errors"] = errors
    return result
