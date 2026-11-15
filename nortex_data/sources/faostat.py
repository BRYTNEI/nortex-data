from datetime import date

import pandas as pd
import requests

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import credential, request

_PORTAL = "https://www.fao.org/faostat/en/#developer-portal"


def _get(settings, path, **params):
    token = credential("FAOSTAT_TOKEN", _PORTAL)
    try:
        response = request("GET", f'{settings["endpoint"]}/{path}', params=params,
                           headers={"Authorization": f"Bearer {token}"})
    except requests.HTTPError as error:
        if error.response.status_code in {401, 403}:
            raise RuntimeError(f"Renueva FAOSTAT_TOKEN en {_PORTAL}") from None
        raise
    return response.json()["data"]


def _codes(settings, domain, dimension):
    return _get(settings, f"codes/{dimension}/{domain}", output_type="json")


def _code_map(records):
    return {str(item["label"]).casefold(): str(item["code"]) for item in records}


def fetch(aoi, start, end, variables=None):
    """Consulta indicadores nacionales de Perú por cultivo y año publicado."""
    selected = variables_for("faostat", variables)
    if not selected:
        return frame()
    settings = config("sources")["faostat"]
    catalog = config("variables")
    rows = []
    domains = sorted({catalog[key]["domain"] for key in selected})
    for domain in domains:
        dimensions = _get(settings, f"dimensions/{domain}/", output_type="json")
        labels = _code_map(dimensions)
        ids = {}
        for key, names in settings["dimensions"].items():
            dimension = next((labels[name] for name in names if name in labels), None)
            if dimension is None:
                raise RuntimeError(f"FAOSTAT {domain}: no se encontró la dimensión {key}")
            ids[key] = dimension
        codes = {key: _code_map(_codes(settings, domain, dim)) for key, dim in ids.items()}
        published = {int(year): code for year, code in codes["year"].items() if year.isdigit()}
        last = min(max(published), date.today().year)
        years = {
            year: code for year, code in published.items()
            if last - 9 <= year <= last
            and (start is None or year >= pd.Timestamp(start).year)
            and (end is None or year <= pd.Timestamp(end).year)
        }
        for key in (key for key in selected if catalog[key]["domain"] == domain):
            element = codes["element"].get(catalog[key]["api"].casefold())
            if element is None:
                raise RuntimeError(f'FAOSTAT {domain}: elemento ausente: {catalog[key]["api"]}')
            country = codes["area"][settings["country"].casefold()]
            for crop in settings["crops"]:
                item = codes["item"].get(crop.casefold())
                if item is None or not years:
                    continue
                params = {
                    f'List{ids["area"]}Codes': country,
                    f'List{ids["item"]}Codes': item,
                    f'List{ids["element"]}Codes': element,
                    f'List{ids["year"]}Codes': list(years.values()),
                }
                data = _get(settings, f"data/{domain}", output_type="json",
                            show_unit="true", show_flags="true", **params)
                for record in data:
                    rows.append(row(
                        aoi, "faostat", f"{domain} / {crop}", key,
                        pd.Timestamp(year=int(record["Year"]), month=1, day=1), record["Value"],
                        record.get("Unit", ""), str(record.get("Flag", "national")),
                    ))
    return frame(rows)
