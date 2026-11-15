"""Pruebas sin red de las fuentes para las decisiones de la v0.7: ENSO, SoilGrids, SRTM,
estación GSOD, POWER horario y datos locales declarados."""

import numpy as np
import pandas as pd
import pytest

from nortex_data.sources import enso, estacion, local, power_horario, soilgrids, srtm
from nortex_data.utils.core import COLUMNS, config, load_aois

AOI = load_aois()["parcela_01"]
CATALOG = config("variables")


# --- ENSO ----------------------------------------------------------------------------

ICEN_TXT = """% Índice Costero El Niño (ICEN; ENFEN, 2024)
% yy   mm   ICEN
2023   6    2.57
2023   7    2.92
"""
ONI_TXT = """ SEAS  YR   TOTAL   ANOM
  DJF 2024  28.07   1.81
  NDJ 2024  26.13  -0.47
"""


def test_icen_parser_ignores_comments():
    assert enso.parse_icen(ICEN_TXT) == [(pd.Timestamp("2023-06-01"), 2.57),
                                         (pd.Timestamp("2023-07-01"), 2.92)]


def test_oni_uses_central_month():
    assert enso.parse_oni(ONI_TXT) == [(pd.Timestamp("2024-01-01"), 1.81),
                                       (pd.Timestamp("2024-12-01"), -0.47)]


def test_enso_fetch_full_record_and_filter(monkeypatch):
    class R:
        def __init__(self, text):
            self.text = text

    monkeypatch.setattr(enso, "request",
                        lambda m, url, **k: R(ICEN_TXT if "ICEN" in url else ONI_TXT))
    out = enso.fetch(AOI, None, None, None)
    assert list(out.columns) == COLUMNS and set(out.variable) == {"icen", "oni"}
    assert out.qc_flag.eq("regional_index").all()
    only = enso.fetch(AOI, "2023-07-15", None, ["icen"])
    assert only.value.tolist() == [2.92]


def test_enso_empty_file_fails():
    with pytest.raises(ValueError):
        enso.parse_icen("% solo comentarios\n")


# --- SoilGrids -----------------------------------------------------------------------

def _geotiff(data, west, north, res):
    from rasterio.io import MemoryFile
    from rasterio.transform import from_origin

    with MemoryFile() as memory:
        with memory.open(driver="GTiff", height=data.shape[0], width=data.shape[1], count=1,
                         dtype="int16", crs="EPSG:4326",
                         transform=from_origin(west, north, res, res)) as dataset:
            dataset.write(data.astype("int16"), 1)
        return memory.read()


def test_soilgrids_nearest_valid_pixel_skips_mask():
    data = np.zeros((3, 3))
    data[0, 2] = 250  # único píxel con dato, en la esquina noreste
    content = _geotiff(data, west=-80.343, north=-5.091, res=0.002)
    value, distance = soilgrids.nearest_valid(content, lat=-5.094, lon=-80.340)
    assert value == 250
    assert 0 < distance < 600


def test_soilgrids_all_masked():
    content = _geotiff(np.zeros((2, 2)), west=-80.343, north=-5.091, res=0.002)
    assert soilgrids.nearest_valid(content, lat=-5.092, lon=-80.342) == (None, None)


def test_soilgrids_fetch_converts_units(monkeypatch):
    content = _geotiff(np.full((2, 2), 280), west=-80.342, north=-5.092, res=0.002)
    monkeypatch.setattr(soilgrids, "_window", lambda *a: content)
    out = soilgrids.fetch(AOI, None, None, ["soil_theta_fc", "soil_clay"])
    fc = out[out.variable == "soil_theta_fc"]
    assert len(fc) == 5 and fc.value.eq(0.28).all()  # 280 ‰ → 0,28 m³/m³, 5 profundidades
    assert out[out.variable == "soil_clay"].value.eq(28.0).all()  # 280 g/kg → 28 %
    assert out.date.isna().all() and out.qc_flag.str.startswith("global_250m").all()


# --- SRTM ----------------------------------------------------------------------------

def test_horn_slope_on_plane():
    # Plano que sube 3 m cada 30 m hacia el este → 10 %
    grid = [[0, 3, 6], [0, 3, 6], [0, 3, 6]]
    assert srtm.horn_slope(grid) == pytest.approx(10.0)
    assert srtm.horn_slope([[5] * 3] * 3) == 0


def test_srtm_point_and_polygon(monkeypatch):
    calls = []

    def fake(settings, points):
        calls.append(len(points))
        return np.array([196.0 + 0.01 * i for i in range(len(points))])

    monkeypatch.setattr(srtm, "_elevations", fake)
    point = srtm.fetch(AOI, None, None, ["elevation", "slope"])
    assert point.set_index("variable").value["elevation"] == pytest.approx(196.04)
    polygon = srtm.fetch(load_aois()["parcela_poligono"], None, None, ["elevation", "relief"])
    assert calls[0] == 9 and calls[-1] >= 4
    assert polygon.qc_flag.str.startswith("polygon_").all()


# --- Estación GSOD ---------------------------------------------------------------------

GSOD_CSV = (
    '"STATION","DATE","MAX","MIN","TEMP","DEWP","PRCP","PRCP_ATTRIBUTES","WDSP"\n'
    '"84401099999","2024-01-01","  95.0","  71.6","  80.0","  65.0"," 0.00","I","  8.0"\n'
    '"84401099999","2024-01-02","9999.9","  70.0","  79.0","  66.0"," 0.50","G","999.9"\n'
)


def test_gsod_conversions_and_missing():
    aoi = {"aoi_id": "x", "lat": -5.2, "lon": -80.6}
    out = estacion.parse_gsod(GSOD_CSV, ["station_tmax", "station_precip", "station_wind"], aoi,
                              "NOAA GSOD", CATALOG, 33.0).set_index(["date", "variable"]).value
    d1, d2 = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")
    assert out[(d1, "station_tmax")] == pytest.approx(35.0)
    assert np.isnan(out[(d1, "station_precip")])  # 0,00 con atributo I = no reportó
    assert out[(d2, "station_precip")] == pytest.approx(12.7)
    assert np.isnan(out[(d2, "station_tmax")]) and np.isnan(out[(d2, "station_wind")])
    assert out[(d1, "station_wind")] == pytest.approx(8 * 0.514444)


# --- POWER horario ---------------------------------------------------------------------

def _hourly_payload(rh_values, t_value=25.0):
    hours = pd.date_range("2024-03-01", periods=len(rh_values), freq="h").strftime("%Y%m%d%H")
    return {
        "header": {"fill_value": -999},
        "parameters": {"T2M": {"units": "C"}, "RH2M": {"units": "%"}},
        "properties": {"parameter": {"T2M": dict.fromkeys(hours, t_value),
                                     "RH2M": dict(zip(hours, rh_values, strict=True))}},
    }


def test_power_hourly_counts_wet_hours():
    payload = _hourly_payload([95] * 5 + [70] * 19)
    out = power_horario.hourly_rows(payload, AOI, ["hours_rh90", "hours_wet_warm"], CATALOG, "p")
    assert out.set_index("variable").value.to_dict() == {"hours_rh90": 5, "hours_wet_warm": 5}
    assert out.qc_flag.eq("derived").all()


def test_power_hourly_incomplete_day_is_missing():
    out = power_horario.hourly_rows(_hourly_payload([95] * 10), AOI, ["hours_rh90"], CATALOG, "p")
    assert np.isnan(out.value.item()) and "incomplete_day" in out.qc_flag.item()


def test_power_hourly_rejects_units():
    payload = _hourly_payload([90] * 24)
    payload["parameters"]["RH2M"]["units"] = "fraction"
    with pytest.raises(ValueError):
        power_horario.hourly_rows(payload, AOI, ["hours_rh90"], CATALOG, "p")


# --- Datos locales declarados --------------------------------------------------------

def test_local_templates_have_required_columns():
    from pathlib import Path

    for name in local.TEMPLATES:
        header = (Path("plantillas") / f"{name}.csv").read_text(encoding="utf-8").splitlines()[0]
        assert header.split(",") == local.template_columns(name), name


def test_local_reads_pcr_ignores_example_and_filters_aoi(tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_LOCAL_DIR", str(tmp_path))
    (tmp_path / "pcr.csv").write_text(
        "fecha_inicio,campania,comision,cultivo,area_autorizada_ha,dotacion_m3_ha,fuente\n"
        "2026-12-01,2026-2027,C1,arroz,1500,12000,EJEMPLO\n"
        "2026-12-01,2026-2027,C1,caupi,300,4000,Junta San Lorenzo\n", encoding="utf-8")
    (tmp_path / "historial.csv").write_text(
        "fecha_siembra,aoi_id,campania,cultivo,fecha_cosecha,rendimiento_t_ha,fuente\n"
        "2025-01-10,parcela_01,2024-2025,arroz,2025-05-20,8.2,usuario\n"
        "2025-01-10,otra,2024-2025,arroz,2025-05-20,9.9,usuario\n", encoding="utf-8")
    out = local.fetch(AOI, None, None, ["water_allocation", "history_yield"])
    values = out.set_index("variable").value.to_dict()
    assert values == {"water_allocation": 4000.0, "history_yield": 8.2}
    assert "Junta San Lorenzo" in out[out.variable == "water_allocation"]["product"].item()
    assert out.qc_flag.str.startswith("declarado").all()


def test_local_missing_file_and_columns(tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_LOCAL_DIR", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="plantillas/reservorio.csv"):
        local.fetch(AOI, None, None, ["reservoir_volume"])
    assert local.fetch(AOI, None, None, None).empty  # sin archivos: aviso, sin error
    (tmp_path / "reservorio.csv").write_text("fecha,volumen\n2026-01-01,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="faltan columnas"):
        local.fetch(AOI, None, None, ["reservoir_volume"])


# --- Reportes hidrológicos de SENAMHI --------------------------------------------------

REPORTE = """INFORMACIÓN HIDROLÓGICA DIARIA 139 - 2022
Jueves, 26 de mayo del 2022       Hora Local       16:00
Chira Poechos  438.30 100 445.50
Chira San Lorenzo 186.04 100 195.60
Jequetepeque Gallito Ciego 366.09 100 366.60
"""


def test_senamhi_report_parser():
    from nortex_data.sources.senamhi_reportes import parse_report

    out = parse_report(REPORTE, {"san_lorenzo": "San Lorenzo", "poechos": "Poechos"})
    by = {r["reservorio"]: r for r in out}
    assert by["san_lorenzo"] == {"reservorio": "san_lorenzo", "date": pd.Timestamp("2022-05-26"),
                                 "volumen": 186.04, "porcentaje": 100.0, "capacidad_util": 195.6}
    assert by["poechos"]["volumen"] == 438.3
    with pytest.raises(ValueError):
        parse_report("sin fecha", {"san_lorenzo": "San Lorenzo"})
