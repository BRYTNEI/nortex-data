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
