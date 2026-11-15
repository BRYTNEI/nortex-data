import os
import time
from io import BytesIO

import pandas as pd
import requests
from dotenv import load_dotenv

from nortex_data.utils.http import request

_PORTAL = "https://urs.earthdata.nasa.gov/"
_LIMIT = 5_000_000


class AppEEARS:
    """Gestiona tareas AppEEARS y consume exclusivamente los CSV de puntos."""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.headers = {}

    def authenticate(self):
        """Obtiene el token de sesión de AppEEARS o lee uno configurado."""
        load_dotenv()
        token = os.getenv("APPEEARS_TOKEN")
        if token:
            self.headers = {"Authorization": f"Bearer {token}"}
            return
        if not (os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD")):
            raise RuntimeError(f"Configura EARTHDATA_USERNAME y EARTHDATA_PASSWORD de {_PORTAL} o APPEEARS_TOKEN.")
        auth = (os.environ["EARTHDATA_USERNAME"], os.environ["EARTHDATA_PASSWORD"])
        try:
            token = request("POST", f"{self.endpoint}/login", auth=auth, retry=False).json()["token"]
        except requests.HTTPError as error:
            if error.response.status_code in {401, 403}:
                raise RuntimeError(f"AppEEARS rechazó el inicio de sesión. Revisa la cuenta en {_PORTAL}") from None
            raise
        self.headers = {"Authorization": f"Bearer {token}"}


    def products(self):
        """Devuelve el catálogo público por identificador de producto."""
        return {
            item["ProductAndVersion"]: item
            for item in request("GET", f"{self.endpoint}/product").json()
        }

    def layers(self, product):
        """Descubre las capas y metadatos de un producto en AppEEARS."""
        return request("GET", f"{self.endpoint}/product/{product}").json()

    def point(self, aoi, start, end, layers):
        """Solicita una tarea de punto y lee los CSV recortados en memoria."""
        if not self.headers:
            self.authenticate()
        payload = {
            "task_type": "point",
            "task_name": "NORTEX",
            "params": {
                "dates": [{"startDate": f"{start:%m-%d-%Y}", "endDate": f"{end:%m-%d-%Y}"}],
                "layers": layers,
                "coordinates": [{"latitude": aoi["lat"], "longitude": aoi["lon"]}],
            },
        }
        task = request("POST", f"{self.endpoint}/task", json=payload,
                       headers=self.headers, retry=False).json()["task_id"]
        deadline = time.monotonic() + 1800
        url = f"{self.endpoint}/task/{task}"
        while time.monotonic() < deadline:
            status = request("GET", url, headers=self.headers).json()["status"].lower()
            if status in {"done", "completed"}:
                break
            if status in {"error", "failed", "cancelled", "canceled"}:
                raise RuntimeError(f"AppEEARS: la tarea {task} terminó con estado {status}")
            time.sleep(15)
        else:
            raise TimeoutError(f"AppEEARS: la tarea {task} sigue pendiente tras 30 minutos")
        bundle = f"{self.endpoint}/bundle/{task}"
        files = request("GET", bundle, headers=self.headers).json()["files"]
        for file in files:
            if file["file_type"] != "csv" or not file["file_name"].endswith("-results.csv"):
                continue
            if file["file_size"] > _LIMIT:
                raise ValueError("AppEEARS: resultado demasiado grande para una consulta puntual")
            response = request("GET", f'{bundle}/{file["file_id"]}', headers=self.headers, stream=True)
            with response:
                content = response.raw.read(_LIMIT + 1, decode_content=True)
            if len(content) > _LIMIT:
                raise ValueError("AppEEARS: CSV fuera del límite de transferencia")
            yield pd.read_csv(BytesIO(content))


def band_column(table, band):
    """Identifica una columna de valores correspondiente a una capa."""
    clean = band.replace("-", "_").lower()
    for name in table:
        candidate = name.replace("-", "_").lower()
        if candidate == clean or candidate.endswith(f"_{clean}"):
            return name
    return None
