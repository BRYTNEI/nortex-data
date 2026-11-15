import logging
import math
import os
import re
from urllib.parse import urlparse

import pandas as pd
import requests
from dotenv import load_dotenv

from nortex_data.derive.extremos import extremos
from nortex_data.utils.blocks import cached_block, concat_blocks
from nortex_data.utils.core import bounds, config, frame, row, variables_for, years
from nortex_data.utils.http import request
from nortex_data.utils.public_zarr import daily_point

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


def _valor_ascii(texto, variable):
    """Extrae valores de un píxel en ASCII de libdap o Hyrax."""
    datos = texto.split("-" * 45, 1)[-1]
    patron = rf"(?m)^[ \t]*([\w.]*)((?:\[[^\]\r\n]*\])+),[ \t]*({_NUMBER})[ \t\r]*$"
    return [float(valor) for nombre, _, valor in re.findall(patron, datos)
            if not nombre or nombre.split(".")[-1] == variable]


def _pixel(url, aoi, headers, variable):
    lon = min(3599, math.floor((aoi["lon"] + 180) * 10))
    lat = min(1799, math.floor((aoi["lat"] + 90) * 10))
    expression = f"{variable}[0:1:0][{lon}:1:{lon}][{lat}:1:{lat}]"
    response = request("GET", f"{url}.ascii?{expression}", headers=headers, stream=True)
    with response:
        payload = response.raw.read(16385, decode_content=True)
    if len(payload) > 16384:
        raise RuntimeError("IMERG: respuesta OPeNDAP fuera del límite para un píxel")
    texto = payload.decode("utf-8", errors="replace")
    if re.search(r"<(?:!doctype\s+html|html\b)", texto[:500], re.IGNORECASE):
        raise RuntimeError("IMERG: OPeNDAP devolvió una página HTML en lugar de datos. Autorice la "
                           "aplicación «NASA GESDISC DATA ARCHIVE» en su perfil de Earthdata.")
    values = _valor_ascii(texto, variable)
    if len(values) != 1:
        # Conserva la estructura del mensaje sin volcar contenido arbitrario del servidor.
        lineas = texto.strip().splitlines()[:8]
        muestra = " | ".join(
            re.sub(r"[^\s\[\]{},:;.]+", "…", linea[:80])
            for linea in lineas
        )[:400]
        raise ValueError(f"IMERG: no se pudo interpretar el píxel OPeNDAP ({len(values)} valores). "
                         f"Inicio de la respuesta: {muestra}")
    value = values[0]
    return value if value >= 0 else float("nan")


def fetch(aoi, start, end, variables=None):
    """Lee un píxel diario por OPeNDAP, priorizando Final sobre Late."""
    selected = variables_for("imerg", variables)
    if not selected:
        return frame()
    settings = config("sources")["imerg"]
    catalog = config("variables")
    start, end = bounds(settings["first"], start, end)
    load_dotenv()
    token = _limpiar_token(os.getenv("EARTHDATA_TOKEN"))
    flag_publico = "daily_utc;run_unspecified"
    if token:
        product = settings["product"]
        try:
            records = _earthdata_records(settings, aoi, start, end, token, catalog["precipitation"]["api"])
            return _with_extremes(records, selected, aoi, catalog, product)
        except requests.HTTPError as error:
            if error.response is None or error.response.status_code not in {401, 403}:
                raise
            logging.getLogger(__name__).warning(
                "IMERG: Earthdata rechazó EARTHDATA_TOKEN (%s). Revise que el token no haya vencido "
                "(dura 60 días), que se copió sin «Bearer» ni espacios, y que la aplicación «NASA GESDISC "
                "DATA ARCHIVE» esté autorizada en su perfil de Earthdata. Se usa la copia pública de "
                "NASA POWER.", error.response.status_code)
            flag_publico += ";auth_error_fallback"
    product = "IMERG / NASA POWER"
    band = settings["public_band"]
    dataset = daily_point(settings["public_zarr"], aoi, start, end, [band])
    records = {
        day: row(aoi, "imerg", product, "precipitation", day, value, "mm/day", flag_publico)
        for day, value in dataset[band].items()
    }
    return _with_extremes(records, selected, aoi, catalog, product)


def _limpiar_token(token):
    """Quita espacios, saltos de línea y un «Bearer » pegado por error."""
    if not token:
        return None
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token or None


def _earthdata_records(settings, aoi, start, end, token, variable):
    headers = {"Authorization": f"Bearer {token}"}

    def block(begin, stop):
        records = {}
        final = dict(_granules(settings, settings["product"], aoi, begin, stop))
        late_start = max(final, default=begin - pd.Timedelta(days=1)) + pd.Timedelta(days=1)
        late = dict(_granules(settings, settings["late"], aoi, late_start, stop)) if late_start <= stop else {}
        for product, flag, granules in [
            (settings["product"], "final", final), (settings["late"], "late", late)
        ]:
            for day, url in granules.items():
                value = _pixel(url, aoi, headers, variable)
                records[day] = row(aoi, "imerg", product, "precipitation", day, value, "mm/day", flag)
        return frame(records.values())

    # Un año cerrado y 100 % Final se guarda en caché: evita repetir ~365 peticiones
    # OPeNDAP por año. Si contiene días Late, se vuelve a pedir hasta que Final los reemplace.
    data = concat_blocks(
        cached_block("imerg", aoi, begin, stop, [settings["product"], settings["version"], variable],
                     block, cacheable=lambda df: not df["qc_flag"].str.contains("late").any())
        for begin, stop in years(start, end)
    )
    return {record[0]: tuple(record) for record in data.itertuples(index=False)}


def _with_extremes(records, selected, aoi, catalog, product):
    data = frame(records.values())
    if data.empty:
        return data
    precipitation = data.set_index("date")["value"]
    summary, monthly = extremos(precipitation)
    if data.qc_flag.str.contains("run_unspecified").any():
        flag = "derived_run_unspecified"
    else:
        flag = "derived_includes_late" if data.qc_flag.str.startswith("late").any() else "derived_final"
    derived = [
        row(aoi, "imerg", product, key, data.date.max(), value, catalog[key]["unit"], flag)
        for key, value in summary.items() if key in selected
    ]
    if "monthly_precip" in selected:
        derived.extend(
            row(aoi, "imerg", product, "monthly_precip", day, value, "mm", flag)
            for day, value in monthly.items() if day >= precipitation.index.min()
        )
    if "precipitation" in selected:
        derived.extend(records.values())
    return frame(derived)
