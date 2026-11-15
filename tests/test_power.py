import json
from pathlib import Path

import pandas as pd
import pytest

from nortex_data.sources import power
from nortex_data.utils.core import COLUMNS, load_aois

# Respuesta real de POWER (San Lorenzo, 1–3 de enero de 2024, community=AG,
# site-elevation=68). Se cambió PRECTOTCORR del día 3 a -999 para probar el relleno.
FIXTURE = Path(__file__).parent / "fixtures" / "power_3dias.json"


@pytest.fixture
def fake_point(monkeypatch):
    """Sustituye la llamada HTTP por la respuesta guardada, ajustada a cada bloque."""
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    calls = []

    def _fake(settings, aoi, begin, stop, codes):
        calls.append((begin, stop, tuple(codes)))
        days = pd.date_range(begin, stop)[:3].strftime("%Y%m%d")
        out = json.loads(json.dumps(payload))
        for name, series in out["properties"]["parameter"].items():
            out["properties"]["parameter"][name] = dict(zip(days, series.values()))
        return out

    monkeypatch.setattr(power, "_point", _fake)
    return calls


@pytest.mark.online
def test_power_san_lorenzo():
    aoi = load_aois()["parcela_01"]
    result = power.fetch(aoi, "2025-01-01", "2025-01-31")
    assert list(result.columns) == COLUMNS
    assert result.groupby("variable").size().eq(31).all()
    assert {"et0", "tmax", "rain_power"} <= set(result.variable)
    assert result[result.variable == "et0"].value.gt(0).all()


def test_power_response_missing_values():
    payload = {
        "parameters": {"ALLSKY": {"units": "MJ/m^2/day"}},
        "header": {"fill_value": -999},
        "properties": {"parameter": {"ALLSKY": {"20250101": 18, "20250102": -999}}},
    }
    result = power._series(payload, {"solar": {"api": "ALLSKY", "unit": "MJ/m^2/day"}})
    assert result.iloc[0].solar == 18
    assert pd.isna(result.iloc[1].solar)


def test_power_unexpected_unit_aborts():
    # EX-14 (v0.7): kWh en lugar de MJ indica una `community` equivocada; no se convierte.
    payload = {
        "parameters": {"ALLSKY": {"units": "kWh/m^2/day"}},
        "header": {"fill_value": -999},
        "properties": {"parameter": {"ALLSKY": {"20250101": 5}}},
    }
    with pytest.raises(ValueError, match="unidad inesperada"):
        power._series(payload, {"solar": {"api": "ALLSKY", "unit": "MJ/m^2/day"}})


def test_power_fetch_offline_schema_et0_and_fill(fake_point, tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    aoi = load_aois()["parcela_01"]
    result = power.fetch(aoi, "2024-01-01", "2024-01-03")
    assert list(result.columns) == COLUMNS
    assert {"tmax", "solar", "rain_power", "et0"} <= set(result.variable)
    et0 = result[result.variable == "et0"]
    assert len(et0) == 3
    assert et0.value.between(3, 9).all()  # rango plausible en la costa norte del Perú
    assert et0.qc_flag.eq("derived").all()
    rain = result[result.variable == "rain_power"].set_index("date").value
    # -999 al final se recorta como «último dato válido»; los días previos quedan
    assert len(rain) == 2


def test_power_yearly_blocks_are_cached(fake_point, tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("NORTEX_CACHE", raising=False)
    aoi = load_aois()["parcela_01"]
    first = power.fetch(aoi, "2023-12-30", "2024-01-02", ["tmax"])
    second = power.fetch(aoi, "2023-12-30", "2024-01-02", ["tmax"])
    assert len(fake_point) == 2  # dos bloques anuales, pedidos una sola vez
    assert [(b.year, s.year) for b, s, _ in fake_point] == [(2023, 2023), (2024, 2024)]
    pd.testing.assert_frame_equal(first, second, check_dtype=False)
    assert len(list(tmp_path.glob("power-bloque-*.parquet"))) == 2


def test_power_cache_can_be_disabled(fake_point, tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("NORTEX_CACHE", "0")
    aoi = load_aois()["parcela_01"]
    power.fetch(aoi, "2024-01-01", "2024-01-02", ["tmax"])
    power.fetch(aoi, "2024-01-01", "2024-01-02", ["tmax"])
    assert len(fake_point) == 2
    assert not list(tmp_path.glob("*.parquet"))
