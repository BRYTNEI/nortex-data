"""Pruebas sin red de IMERG, SMAP, Sentinel-2, GAEZ y FAOSTAT.

Las respuestas simulan el formato de cada API (OPeNDAP ASCII, CMR UMM-JSON, Statistical API
de CDSE, ArcGIS ImageServer y FAOSTAT) para validar el parseo y el esquema común.
"""

import numpy as np
import pandas as pd
import pytest

from nortex_data.sources import faostat, gaez, imerg, s2, s2_cog, smap
from nortex_data.utils.core import COLUMNS, config, load_aois

AOI = load_aois()["parcela_01"]


class _Raw:
    def __init__(self, payload):
        self.payload = payload

    def read(self, size, decode_content=True):
        return self.payload[:size]


class _Response:
    """Respuesta mínima compatible con `request(..., stream=True)` y `.json()`."""

    def __init__(self, payload=b"", document=None):
        self.raw = _Raw(payload)
        self.document = document

    def json(self):
        return self.document

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


# --- IMERG ---------------------------------------------------------------------------

OPENDAP_ASCII = (
    b"Dataset {\n    Float32 precipitation[time = 1][lon = 1][lat = 1];\n} 3B-DAY;\n"
    b"---------------------------------------------\n"
    b"precipitation.precipitation[1][1][1]\n"
    b"[0][0], 12.5\n"
)


def test_imerg_pixel_requests_single_index(monkeypatch):
    urls = []

    def fake_request(method, url, **kwargs):
        urls.append(url)
        return _Response(OPENDAP_ASCII)

    monkeypatch.setattr(imerg, "request", fake_request)
    value = imerg._pixel("https://gpm1.gesdisc.eosdis.nasa.gov/opendap/x.nc4", AOI, {}, "precipitation")
    assert value == 12.5
    # lon −80,34 → índice 996; lat −5,09 → índice 849 en la malla de 0,1°
    assert urls[0].endswith(".ascii?precipitation[0:1:0][996:1:996][849:1:849]")


def test_imerg_pixel_negative_is_missing(monkeypatch):
    monkeypatch.setattr(imerg, "request",
                        lambda *a, **k: _Response(OPENDAP_ASCII.replace(b"12.5", b"-9999.9")))
    assert np.isnan(imerg._pixel("https://x.nasa.gov/a", AOI, {}, "precipitation"))


def test_imerg_granules_keep_opendap_link(monkeypatch):
    granule = {"umm": {
        "TemporalExtent": {"RangeDateTime": {"BeginningDateTime": "2024-01-02T00:00:00.000Z"}},
        "RelatedUrls": [
            {"URL": "https://data.gesdisc.earthdata.nasa.gov/x.nc4", "Type": "GET DATA"},
            {"URL": "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/x.nc4.html",
             "Subtype": "OPENDAP DATA"},
        ],
    }}
    monkeypatch.setattr(imerg, "request", lambda *a, **k: _Response(document={"items": [granule]}))
    settings = config("sources")["imerg"]
    found = list(imerg._granules(settings, "GPM_3IMERGDF", AOI,
                                 pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-31")))
    assert found == [(pd.Timestamp("2024-01-02"), "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/x.nc4")]


def test_imerg_public_route_with_extremes(monkeypatch, tmp_path):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("EARTHDATA_TOKEN", raising=False)
    monkeypatch.setattr(imerg, "load_dotenv", lambda: None)
    days = pd.date_range("2024-01-01", "2024-01-31")
    rain = pd.Series(0.0, index=days)
    rain.iloc[[3, 10, 20]] = [5.0, 30.0, 2.0]
    monkeypatch.setattr(imerg, "daily_point",
                        lambda root, aoi, b, e, bands: pd.DataFrame({bands[0]: rain.loc[b:e]}))
    out = imerg.fetch(AOI, "2024-01-01", "2024-01-31",
                      ["precipitation", "rx1day", "days_gt_p95", "monthly_precip"])
    assert list(out.columns) == COLUMNS
    assert out[out.variable == "rx1day"].value.item() == 30.0
    assert out[out.variable == "days_gt_p95"].value.item() == 1
    assert out[out.variable == "monthly_precip"].value.item() == pytest.approx(37.0)
    assert out[out.variable == "precipitation"].qc_flag.eq("daily_utc;run_unspecified").all()


# --- SMAP ----------------------------------------------------------------------------

def test_smap_public_route_schema_and_yearly_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("NORTEX_CACHE", raising=False)
    for name in ("APPEEARS_TOKEN", "EARTHDATA_USERNAME", "EARTHDATA_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(smap, "load_dotenv", lambda: None)
    calls = []

    def fake_point(root, aoi, begin, stop, bands):
        calls.append((begin, stop))
        index = pd.date_range(begin, stop)
        return pd.DataFrame({band: 0.2 for band in bands}, index=index)

    monkeypatch.setattr(smap, "daily_point", fake_point)
    first = smap.fetch(AOI, "2023-12-30", "2024-01-02", ["sm_surface", "sm_rootzone"])
    smap.fetch(AOI, "2023-12-30", "2024-01-02", ["sm_surface", "sm_rootzone"])
    assert list(first.columns) == COLUMNS
    assert len(first) == 8  # 4 días × 2 variables
    assert first.qc_flag.eq("daily_utc;qc_unavailable").all()
    assert len(calls) == 2  # un bloque por año, la segunda consulta sale de la caché


def test_smap_appeears_rows_average_three_hourly(monkeypatch):
    table = pd.DataFrame({
        "Date": ["2024-01-01T01:30:00", "2024-01-01T04:30:00", "2024-01-02T01:30:00"],
        "SPL4SMGP_008_Geophysical_Data_sm_surface": [0.10, 0.20, -9999],
    })
    catalog = config("variables")
    rows = list(smap._daily_rows(AOI, [table], {"sm_surface": "Geophysical_Data_sm_surface"},
                                 [], {"Geophysical_Data_sm_surface": {}}, "SPL4SMGP.008", catalog))
    first, second = rows
    assert first[7] == pytest.approx(0.15) and first[9] == "samples=2;qc_unavailable"
    assert np.isnan(second[7]) and second[9] == "samples=0;qc_unavailable;missing"


# --- Sentinel-2 ----------------------------------------------------------------------

def test_s2_statistics_response_parsing():
    document = {"status": "OK", "data": [
        {"interval": {"from": "2024-01-05T00:00:00Z", "to": "2024-01-06T00:00:00Z"},
         "outputs": {"ndre": {"bands": {"B0": {"stats": {
             "min": 0.1, "max": 0.5, "mean": 0.3, "stDev": 0.05,
             "sampleCount": 100, "noDataCount": 20,
             "percentiles": {"10.0": 0.25, "50.0": 0.3, "90.0": 0.35}}}}}}},
        {"interval": {"from": "2024-01-10T00:00:00Z", "to": "2024-01-11T00:00:00Z"},
         "error": {"type": "NO_DATA"}},
    ]}
    settings, catalog = config("sources")["s2"], config("variables")
    rows = list(s2.statistics_rows(AOI, document, ["ndre", "ndre_p10", "ndre_count"],
                                   settings, catalog))
    values = {r[6]: r[7] for r in rows}
    assert values == {"ndre": 0.3, "ndre_p10": 0.25, "ndre_count": 80}
    assert {r[0] for r in rows} == {pd.Timestamp("2024-01-05")}


def test_s2_statistics_error_raises():
    document = {"status": "OK", "data": [
        {"interval": {"from": "2024-01-05T00:00:00Z"}, "error": {"type": "EXECUTION_ERROR"}}]}
    with pytest.raises(RuntimeError):
        list(s2.statistics_rows(AOI, document, ["ndre"], config("sources")["s2"],
                                config("variables")))


def test_s2_public_sample_summary():
    catalog = config("variables")
    samples = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    rows = {r[6]: r for r in s2_cog.sample_rows(AOI, pd.Timestamp("2024-01-05"), samples,
                                                ["ndre", "ndre_median", "ndre_count"], catalog)}
    assert rows["ndre"][7] == pytest.approx(0.3)
    assert rows["ndre_median"][7] == pytest.approx(0.3)
    assert rows["ndre_count"][7] == 5 and rows["ndre"][9] == "cog_window"
    empty = {r[6]: r for r in s2_cog.sample_rows(AOI, pd.Timestamp("2024-01-06"), np.array([]),
                                                 ["ndre", "ndre_count"], catalog)}
    assert np.isnan(empty["ndre"][7]) and empty["ndre_count"][7] == 0
    assert empty["ndre_count"][9] == "cog_no_valid_pixels"


# --- GAEZ ----------------------------------------------------------------------------

def test_gaez_identify_one_pixel_per_layer(monkeypatch):
    calls = []

    def fake_arcgis(url, **params):
        calls.append(url)
        if url.endswith("/query"):
            return {"features": [{"attributes": {
                "objectid": 288, "crop": "Wetland rice", "year": "1981-2010", "model": "CRUTS32",
                "rcp": "Historical", "input_level": "High", "water_supply": "Gravity Irrigation",
                "c02_fertilization": "", "units": "class"}}]}
        return {"value": "4"}

    monkeypatch.setattr(gaez, "_arcgis", fake_arcgis)
    out = gaez.fetch(AOI, None, None, ["suitability"])
    assert list(out.columns) == COLUMNS
    assert out.value.tolist() == [4.0]
    assert out["product"].item().startswith("GAEZ v4 / Wetland rice / 1981-2010")
    assert out.date.isna().all()  # capas por periodo climático, sin fecha de observación
    assert sum(url.endswith("/identify") for url in calls) == 1


# --- FAOSTAT -------------------------------------------------------------------------

class _FakeFaostat:
    def __init__(self, settings):
        self.requests = []

    def get(self, path, **params):
        self.requests.append((path, params))
        if path.startswith("dimensions/"):
            return [{"label": "Year", "code": "year"}, {"label": "Area", "code": "area"},
                    {"label": "Item", "code": "item"}, {"label": "Element", "code": "element"}]
        if path.startswith("codes/year"):
            return [{"label": str(y), "code": str(y)} for y in range(2010, 2024)]
        if path.startswith("codes/area"):
            return [{"label": "Peru", "code": "170"}]
        if path.startswith("codes/item"):
            return [{"label": "Rice", "code": "27"}]
        if path.startswith("codes/element"):
            return [{"label": "Production", "code": "5510"}]
        return [{"Year": "2023", "Value": "3400000", "Unit": "t", "Flag": "A"}]


def test_faostat_discovers_codes_and_limits_ten_years(monkeypatch):
    clients = []

    def factory(settings):
        clients.append(_FakeFaostat(settings))
        return clients[0]

    monkeypatch.setattr(faostat, "_Client", factory)
    out = faostat.fetch(AOI, None, None, ["production"])
    assert list(out.columns) == COLUMNS
    assert out.value.tolist() == [3400000.0] and out.unit.tolist() == ["t"]
    assert out.date.tolist() == [pd.Timestamp("2023-01-01")]
    data_calls = [params for path, params in clients[0].requests if path.startswith("data/")]
    assert len(data_calls) == 1  # mango y limón no están en los códigos simulados
    years = data_calls[0]["ListyearCodes"].split(",")
    assert years == [str(y) for y in range(2014, 2024)]  # últimos 10 años publicados


def test_imerg_token_rechazado_usa_respaldo_publico(monkeypatch, tmp_path):
    import requests

    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("EARTHDATA_TOKEN", "  Bearer token-vencido\n")
    monkeypatch.setattr(imerg, "load_dotenv", lambda: None)
    vistos = []

    def rechazar(settings, aoi, start, end, token, variable):
        vistos.append(token)
        respuesta = requests.Response()
        respuesta.status_code = 403
        raise requests.HTTPError("403", response=respuesta)

    monkeypatch.setattr(imerg, "_earthdata_records", rechazar)
    dias = pd.date_range("2024-01-01", "2024-01-10")
    monkeypatch.setattr(imerg, "daily_point",
                        lambda root, aoi, b, e, bands: pd.DataFrame({bands[0]: 1.0}, index=dias))
    out = imerg.fetch(AOI, "2024-01-01", "2024-01-10", ["precipitation"])
    assert vistos == ["token-vencido"]  # se limpió «Bearer », espacios y salto de línea
    assert out.qc_flag.str.contains("auth_error_fallback").all()
    assert (out["product"] == "IMERG / NASA POWER").all()
