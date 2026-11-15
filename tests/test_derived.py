import pandas as pd
import pytest

from nortex_data.derive.esi import anomaly, esi
from nortex_data.derive.extremos import extremos


def test_esi_and_anomaly():
    index = esi(pd.Series([1, 3, 4]), pd.Series([4, 4, 0]))
    assert index.iloc[:2].tolist() == [0.25, 0.75]
    assert pd.isna(index.iloc[2])
    assert anomaly(index).iloc[:2].tolist() == [-1, 1]
    assert anomaly(pd.Series([1, 1])).isna().all()


def test_extremes_respect_missing_days():
    series = pd.Series([0, 0, 1, 2, 3, 4, 5], index=pd.date_range("2025-01-01", periods=7))
    metrics, monthly = extremos(series)
    assert metrics["rx5day"] == 15
    assert metrics["max_dry_days"] == 2
    assert metrics["days_gt_p95"] == 1
    assert pd.isna(monthly.iloc[0])
    metrics, _ = extremos(series.drop(series.index[4]))
    assert metrics["rx1day"] == pytest.approx(5)
    assert pd.isna(metrics["rx5day"])


def test_extremes_percentiles_use_wet_days_only():
    # Clima seco: 95 días sin lluvia y 5 días húmedos. Con todos los días el p95 sería
    # ~0,1 mm y contaría los 5 días; con días húmedos (>= 1 mm) solo supera el evento mayor.
    values = [0.0] * 95 + [2.0, 4.0, 6.0, 8.0, 50.0]
    series = pd.Series(values, index=pd.date_range("2025-01-01", periods=100))
    metrics, _ = extremos(series)
    assert metrics["days_gt_p95"] == 1
    assert metrics["days_gt_p99"] == 1
    assert metrics["max_dry_days"] == 95


def test_extremes_without_wet_days():
    series = pd.Series([0.0, 0.2, 0.0], index=pd.date_range("2025-01-01", periods=3))
    metrics, _ = extremos(series)
    assert pd.isna(metrics["days_gt_p95"])
    assert metrics["max_dry_days"] == 3
