from datetime import date

import pandas as pd
import pytest

from nortex_data.sources.ecostress import _et_conversion
from nortex_data.utils.blocks import cached_block
from nortex_data.utils.core import bounds, frame, load_aois, row, years

TODAY = pd.Timestamp(date.today())


# --- Regla «todo el registro o máximo 10 años» ---------------------------------------

def test_long_source_is_capped_to_ten_years():
    lower, upper = bounds("1981-01-01")
    assert lower == TODAY - pd.DateOffset(years=10)
    assert upper == TODAY


def test_short_source_uses_full_record():
    first = TODAY - pd.DateOffset(years=5)
    lower, _ = bounds(first)
    assert lower == first


def test_explicit_start_never_before_source_or_window():
    lower, upper = bounds("2018-07-09", "2010-01-01", "2030-01-01")
    assert lower == max(pd.Timestamp("2018-07-09"), TODAY - pd.DateOffset(years=10))
    assert upper == TODAY  # nunca después de hoy


def test_years_split_inclusive_blocks():
    blocks = list(years(pd.Timestamp("2022-11-15"), pd.Timestamp("2024-02-01")))
    assert [(b.date().isoformat(), e.date().isoformat()) for b, e in blocks] == [
        ("2022-11-15", "2022-12-31"),
        ("2023-01-01", "2023-12-31"),
        ("2024-01-01", "2024-02-01"),
    ]


# --- Zonas de estudio --------------------------------------------------------------

def test_example_aois_load():
    aois = load_aois()
    assert {"parcela_01", "parcela_poligono"} <= set(aois)
    polygon = aois["parcela_poligono"]
    assert -80.341 <= polygon["lon"] <= -80.340
    assert -5.094 <= polygon["lat"] <= -5.093


def _write(tmp_path, coordinates):
    path = tmp_path / "aois.yaml"
    ring = ", ".join(f"[{x}, {y}]" for x, y in coordinates)
    path.write_text(
        "aois:\n  zona:\n    geometry:\n      type: Polygon\n"
        f"      coordinates: [[{ring}]]\n",
        encoding="utf-8",
    )
    return path


def test_large_polygon_is_rejected(tmp_path):
    path = _write(tmp_path, [(-81, -6), (-80, -6), (-80, -5), (-81, -5), (-81, -6)])
    with pytest.raises(ValueError, match="excede"):
        load_aois(path)


def test_self_intersecting_polygon_is_rejected(tmp_path):
    bowtie = [(-80.34, -5.09), (-80.33, -5.08), (-80.34, -5.08), (-80.33, -5.09), (-80.34, -5.09)]
    with pytest.raises(ValueError, match="inválido"):
        load_aois(_write(tmp_path, bowtie))


def test_fill_values_become_missing():
    aoi = {"aoi_id": "x", "lat": 0.0, "lon": 0.0}
    data = frame([row(aoi, "s", "p", "v", "2024-01-01", -9999, "u"),
                  row(aoi, "s", "p", "v", "2024-01-02", 3, "u")])
    assert pd.isna(data.value.iloc[0]) and data.qc_flag.iloc[0] == "missing"
    assert data.value.iloc[1] == 3 and data.qc_flag.iloc[1] == "ok"


# --- Caché por bloques ---------------------------------------------------------------

def _producer(calls, flag="final"):
    aoi = {"aoi_id": "x", "lat": 0.0, "lon": 0.0}

    def produce(begin, stop):
        calls.append((begin, stop))
        return frame([row(aoi, "imerg", "p", "precipitation", begin, 1.0, "mm/day", flag)])

    return aoi, produce


def test_closed_block_is_cached(tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("NORTEX_CACHE", raising=False)
    calls = []
    aoi, produce = _producer(calls)
    begin, stop = pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")
    cached_block("imerg", aoi, begin, stop, ["v"], produce)
    cached_block("imerg", aoi, begin, stop, ["v"], produce)
    assert len(calls) == 1


def test_recent_block_is_not_cached(tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    calls = []
    aoi, produce = _producer(calls)
    begin = TODAY - pd.Timedelta(days=30)
    cached_block("imerg", aoi, begin, TODAY, ["v"], produce)
    cached_block("imerg", aoi, begin, TODAY, ["v"], produce)
    assert len(calls) == 2


def test_provisional_block_is_not_cached(tmp_path, monkeypatch):
    monkeypatch.setenv("NORTEX_CACHE_DIR", str(tmp_path))
    calls = []
    aoi, produce = _producer(calls, flag="late")
    begin, stop = pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")
    no_late = lambda df: not df["qc_flag"].str.contains("late").any()  # noqa: E731
    cached_block("imerg", aoi, begin, stop, ["v"], produce, cacheable=no_late)
    cached_block("imerg", aoi, begin, stop, ["v"], produce, cacheable=no_late)
    assert len(calls) == 2


# --- Unidades de ECOSTRESS ETdaily ---------------------------------------------------

@pytest.mark.parametrize(
    ("units", "mode", "flag"),
    [
        ("W/m^2", "flux", "clear"),
        ("W m-2", "flux", "clear"),
        ("mm/day", "depth", "clear"),
        (None, "flux", "clear;units_assumed_w_m2"),
    ],
)
def test_et_conversion_by_declared_unit(units, mode, flag):
    assert _et_conversion(units) == (mode, flag)


def test_et_conversion_rejects_unknown_unit():
    with pytest.raises(ValueError, match="no reconocida"):
        _et_conversion("kg/m^2/s")
