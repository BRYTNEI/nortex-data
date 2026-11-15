import hashlib
import json
import logging
import os
from pathlib import Path
from uuid import uuid4

import pandas as pd

from nortex_data.utils.core import COLUMNS, frame

# Días recientes que no se guardan: la fuente aún puede completarlos o corregirlos.
RECENT_DAYS = 10
_log = logging.getLogger(__name__)


def _enabled():
    return os.getenv("NORTEX_CACHE") != "0"


def cached_block(source, aoi, begin, stop, params, producer, cacheable=None):
    """Devuelve un bloque (normalmente un año) desde caché o lo produce y lo guarda.

    Solo se guardan bloques cerrados, cuyo fin es anterior a hoy menos ``RECENT_DAYS``.
    Así las consultas por defecto (últimos 10 años hasta hoy) reutilizan los años ya
    descargados y solo vuelven a pedir el tramo reciente. Se guardan únicamente tablas
    recortadas en el esquema común; nunca archivos crudos.

    ``cacheable(df) -> bool`` permite excluir bloques provisionales (p. ej. días IMERG
    Late que luego serán reemplazados por Final).
    """
    closed = stop < pd.Timestamp.today().normalize() - pd.Timedelta(days=RECENT_DAYS)
    if not (_enabled() and closed):
        return producer(begin, stop)
    key = json.dumps(
        [source, aoi["aoi_id"], aoi["lat"], aoi["lon"], aoi.get("elevation_m"),
         str(pd.Timestamp(begin).date()), str(pd.Timestamp(stop).date()), params],
        sort_keys=True, default=str,
    )
    path = Path(os.getenv("NORTEX_CACHE_DIR", "cache")) / (
        f"{source}-bloque-{hashlib.sha256(key.encode()).hexdigest()[:24]}.parquet"
    )
    if path.is_file():
        return pd.read_parquet(path)
    result = producer(begin, stop)
    if result.empty or (cacheable is not None and not cacheable(result)):
        return result
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.stem}-{uuid4().hex}.tmp")
    try:
        result.to_parquet(temporary, index=False)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    _log.debug("Bloque guardado en caché: %s", path)
    return result


def concat_blocks(blocks):
    """Une bloques en el esquema común y en orden estable."""
    blocks = [block for block in blocks if not block.empty]
    if not blocks:
        return frame()
    result = pd.concat(blocks, ignore_index=True)[COLUMNS]
    result["date"] = pd.to_datetime(result["date"])
    result["value"] = pd.to_numeric(result["value"])
    return result.sort_values(["date", "aoi_id", "source", "variable"], ignore_index=True)
