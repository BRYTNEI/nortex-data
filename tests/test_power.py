import pandas as pd
import pytest

from nortex_data.sources import power
from nortex_data.utils.core import COLUMNS, load_aois


@pytest.mark.online
def test_power_san_lorenzo():
    aoi = load_aois()["parcela_01"]
    result = power.fetch(aoi, "2025-01-01", "2025-01-31")
    assert list(result.columns) == COLUMNS
    assert result.groupby("variable").size().eq(31).all()
    assert {"et0", "tmax", "rain_power"} <= set(result.variable)
    assert result[result.variable == "et0"].value.gt(0).all()


def test_power_response_units_and_missing():
    payload = {
        "parameters": {"ALLSKY": {"units": "kWh/m^2/day"}},
        "header": {"fill_value": -999},
        "properties": {"parameter": {"ALLSKY": {"20250101": 5, "20250102": -999}}},
    }
    result = power._series(payload, {"solar": {"api": "ALLSKY", "unit": "MJ/m^2/day"}})
    assert result.iloc[0].solar == 18
    assert pd.isna(result.iloc[1].solar)
