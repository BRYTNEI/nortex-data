import numpy as np
import pandas as pd
from numcodecs import get_codec

from nortex_data.utils.http import request

_MAX_BYTES = 16 * 1024**2


def _chunk(root, array, metadata, indices):
    info = metadata[f"{array}/.zarray"]
    chunks = tuple(info["chunks"])
    key = info.get("dimension_separator", ".").join(map(str, indices))
    with request("GET", f"{root}/{array}/{key}", stream=True) as response:
        encoded = response.raw.read(_MAX_BYTES + 1, decode_content=True)
    if len(encoded) > _MAX_BYTES:
        raise ValueError(f"Bloque Zarr demasiado grande: {array}")
    data = encoded
    if info["compressor"]:
        data = get_codec(info["compressor"]).decode(data)
    for filter_config in reversed(info["filters"] or []):
        data = get_codec(filter_config).decode(data)
    return np.frombuffer(data, dtype=info["dtype"]).reshape(chunks, order=info["order"])


def daily_point(root, aoi, start, end, bands):
    """Lee coordenadas y bloques temporales de un único punto en un Zarr diario."""
    if start > end or not bands:
        return pd.DataFrame(columns=bands)
    metadata = request("GET", f"{root}/.zmetadata").json()["metadata"]
    epoch = metadata["time/.zattrs"]["units"]
    if not epoch.startswith("days since "):
        raise ValueError(f"Unidad temporal Zarr inesperada: {epoch}")
    offsets = _chunk(root, "time", metadata, (0,))
    dates = pd.DatetimeIndex(pd.to_datetime(offsets, unit="D", origin=epoch.removeprefix("days since ")))
    positions = np.flatnonzero((dates >= start) & (dates <= end))
    result = pd.DataFrame(index=dates[positions])
    if not len(positions):
        return result.reindex(columns=bands)
    latitudes = _chunk(root, "lat", metadata, (0,))
    longitudes = _chunk(root, "lon", metadata, (0,))
    if not latitudes.min() <= aoi["lat"] <= latitudes.max():
        return pd.DataFrame(columns=bands)
    latitude = int(np.abs(latitudes - aoi["lat"]).argmin())
    distance = np.abs((longitudes - aoi["lon"] + 180) % 360 - 180)
    longitude = int(distance.argmin())
    for band in bands:
        attrs = metadata[f"{band}/.zattrs"]
        if attrs["_ARRAY_DIMENSIONS"] != ["time", "lat", "lon"]:
            raise ValueError(f"Dimensiones Zarr inesperadas para {band}")
        temporal, ny, nx = metadata[f"{band}/.zarray"]["chunks"]
        block_ids = positions // temporal
        samples = np.full(len(positions), np.nan)
        for block_id in np.unique(block_ids):
            block = _chunk(root, band, metadata, (block_id, latitude // ny, longitude // nx))
            mask = block_ids == block_id
            samples[mask] = block[positions[mask] % temporal, latitude % ny, longitude % nx]
        series = pd.Series(samples, index=result.index)
        result[band] = series.where(series.between(attrs.get("valid_min", 0), attrs.get("valid_max", np.inf)))
    return result.loc[:result.last_valid_index()] if result.notna().any().any() else result.iloc[:0]
