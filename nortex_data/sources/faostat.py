import os
from datetime import date

import pandas as pd
import requests
from dotenv import load_dotenv

from nortex_data.utils.core import config, frame, row, variables_for
from nortex_data.utils.http import request

_PORTAL = "https://www.fao.org/faostat/en/#developer-portal"


class _Client:
    def __init__(self, settings):
        load_dotenv()
        self.settings = settings
        self.token = os.getenv("FAOSTAT_TOKEN")
        self.username = os.getenv("FAOSTAT_USERNAME")
        self.password = os.getenv("FAOSTAT_PASSWORD")
        if not self.token:
            self.login()

    def login(self):
        if not (self.username and self.password):
            raise RuntimeError(
                f"Configura FAOSTAT_TOKEN vigente o FAOSTAT_USERNAME y FAOSTAT_PASSWORD. {_PORTAL}"
            )
        try:
            payload = request(
                "POST", self.settings["login"],
                data={"username": self.username, "password": self.password}, retry=False,
            ).json()
        except requests.HTTPError as error:
            if error.response.status_code in {400, 401, 403}:
                raise RuntimeError(f"FAOSTAT rechazó el inicio de sesión. Revisa la cuenta en {_PORTAL}") from None
            raise
        result = payload.get("data", payload)
        result = result.get("AuthenticationResult", result)
        self.token = result.get("AccessToken") or result.get("access_token")
        if not self.token:
            raise RuntimeError("FAOSTAT: la respuesta de inicio de sesión no contiene AccessToken")

    def get(self, path, **params):
        url = f'{self.settings["endpoint"]}/{path}'
        for attempt in range(2):
            try:
                response = request("GET", url, params=params,
                                   headers={"Authorization": f"Bearer {self.token}"})
                return response.json()["data"]
            except requests.HTTPError as error:
                if error.response.status_code not in {401, 403}:
                    raise
                if attempt or not (self.username and self.password):
                    raise RuntimeError(f"FAOSTAT rechazó el token. Renueva FAOSTAT_TOKEN en {_PORTAL}") from None
                self.login()

def _code_map(records):
    """Mapa etiqueta → código; admite registros planos y con ``subdimensions``.

    En las subdimensiones el código viene en ``id`` (o ``code``); en los registros planos, en
    ``code``. Se ignoran los registros sin etiqueta o sin código.
    """
    result = {}
    for item in records:
        if item.get("subdimensions"):
            for subdimension in item["subdimensions"]:
                label = subdimension.get("label")
                code = subdimension.get("id") or subdimension.get("code")
                if label is not None and code is not None:
                    result[str(label).casefold()] = str(code)
        else:
            label = item.get("label")
            code = item.get("code")
            if label is not None and code is not None:
                result[str(label).casefold()] = str(code)
    return result


def fetch(aoi, start, end, variables=None):
    """Consulta indicadores nacionales de Perú por cultivo y año publicado."""
    selected = variables_for("faostat", variables)
    if not selected:
        return frame()
    settings = config("sources")["faostat"]
    catalog = config("variables")
    client = _Client(settings)
    rows = []
    domains = sorted({catalog[key]["domain"] for key in selected})
    for domain in domains:
        dimensions = client.get(f"dimensions/{domain}/", output_type="json")
        labels = _code_map(dimensions)
        ids = {}
        for key, names in settings["dimensions"].items():
            dimension = next((labels[name] for name in names if name in labels), None)
            if dimension is None:
                raise RuntimeError(f"FAOSTAT {domain}: no se encontró la dimensión {key}")
            ids[key] = dimension
        codes = {key: _code_map(client.get(f"codes/{dim}/{domain}", output_type="json")) for key, dim in ids.items()}
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
                    f'List{ids["year"]}Codes': ",".join(years.values()),
                }
                data = client.get(f"data/{domain}", output_type="json",
                            show_unit="true", show_flags="true", **params)
                for record in data:
                    rows.append(row(
                        aoi, "faostat", f"{domain} / {crop}", key,
                        pd.Timestamp(year=int(record["Year"]), month=1, day=1), record["Value"],
                        record.get("Unit", ""), str(record.get("Flag", "national")),
                    ))
    return frame(rows)
