from nortex_data.sources.ecostress import import_point_csv
from nortex_data.utils.core import load_aois


def test_app_eeears_csv_filters_clouds_and_fill(tmp_path):
    csv = tmp_path / "pilot-ECO_L2T_LSTE-002-results.csv"
    csv.write_text(
        "Date,ECO_L2T_LSTE_002_LST,ECO_L2T_LSTE_002_cloud\n"
        "2025-01-01,302.5,0\n2025-01-02,303,1\n2025-01-03,-9999,0\n",
        encoding="utf-8",
    )

    result = import_point_csv(load_aois()["parcela_01"], [csv], ["lst"])

    assert result.variable.tolist() == ["lst"]
    assert result.value.tolist() == [302.5]
    assert result.unit.tolist() == ["K"]
